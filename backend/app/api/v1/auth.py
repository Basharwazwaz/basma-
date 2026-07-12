from datetime import datetime, timezone
from urllib.parse import urlencode
import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.limiter import limiter
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
)
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Users, Profiles
from app.models.auth import RefreshTokens
from app.schemas.auth import Token, ForgotPassword, ResetPassword
from app.schemas.user import UserCreate, UserResponse
from app.services.email import send_reset_password_email

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


async def _issue_tokens_for_user(
    user: Users, response: Response, db: AsyncSession
) -> dict:
    """Create access + refresh tokens, persist the refresh token, set the cookie."""
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    decoded = decode_token(refresh_token)
    db_token = RefreshTokens(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.fromtimestamp(decoded["exp"], tz=timezone.utc),
    )
    db.add(db_token)
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).where(Users.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = Users(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.flush()

    profile = Profiles(
        user_id=user.id,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(profile)
    await db.commit()

    result = await db.execute(
        select(Users).options(selectinload(Users.profile)).where(Users.id == user.id)
    )
    return result.scalars().first()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    result = await db.execute(select(Users).where(Users.email == form_data.username))
    user = result.scalars().first()

    # Reject OAuth-only users (placeholder password starts with "!")
    if user and user.hashed_password.startswith("!"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google login. Please sign in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await _issue_tokens_for_user(user, response, db)


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    result = await db.execute(
        select(RefreshTokens).where(RefreshTokens.token == refresh_token)
    )
    db_token = result.scalars().first()

    if not db_token or db_token.is_revoked:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Check user exists and is active
    user_result = await db.execute(select(Users).where(Users.id == user_id))
    user = user_result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or deactivated")

    new_access_token = create_access_token(subject=user_id)
    return {"access_token": new_access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        result = await db.execute(
            select(RefreshTokens).where(RefreshTokens.token == refresh_token)
        )
        db_token = result.scalars().first()
        if db_token:
            db_token.is_revoked = True
            await db.commit()

    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}


# ---------------------------------------------------------------------------
# Forgot / Reset Password
# ---------------------------------------------------------------------------

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPassword, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).where(Users.email == data.email))
    user = result.scalars().first()
    # Return the same message regardless to prevent email enumeration attacks
    if not user:
        return {"message": "If that email is in our system, we sent a reset link."}

    # 1-hour reset token
    reset_token = create_reset_token(subject=user.id)
    await send_reset_password_email(email_to=user.email, reset_token=reset_token)
    return {"message": "If that email is in our system, we sent a reset link."}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPassword, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.token)
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("No subject in token")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.new_password)

    # Revoke all existing refresh tokens on password change for security
    tokens_result = await db.execute(
        select(RefreshTokens).where(RefreshTokens.user_id == user.id)
    )
    for token in tokens_result.scalars().all():
        token.is_revoked = True

    await db.commit()
    return {"message": "Password reset successfully"}


# ---------------------------------------------------------------------------
# Google OAuth — Step 1: Redirect to Google's consent screen
# ---------------------------------------------------------------------------

@router.get("/google")
async def google_login():
    """
    Redirect the browser to Google's OAuth 2.0 consent screen.
    The client_id and redirect_uri come entirely from environment variables.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured on this server.",
        )

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


# ---------------------------------------------------------------------------
# Google OAuth — Step 2: Handle the authorization code callback
# ---------------------------------------------------------------------------

@router.get("/google/callback")
async def google_callback(
    code: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
    error: str = None,
):
    """
    Google redirects here with ?code=... after the user consents.
    We exchange the code for tokens, fetch the user's Google profile,
    then create-or-login the user and issue our own JWTs.
    """
    if error:
        raise HTTPException(status_code=400, detail="Google OAuth error")

    async with httpx.AsyncClient() as client:
        # --- Exchange authorization code for Google tokens ---
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange code with Google",
            )

        google_tokens = token_response.json()
        google_access_token = google_tokens.get("access_token")

        if not google_access_token:
            raise HTTPException(
                status_code=400,
                detail="No access token received from Google.",
            )

        # --- Fetch the authenticated user's Google profile ---
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch user info from Google.",
            )

        google_user = userinfo_response.json()

    google_email: str = google_user.get("email")
    if not google_email:
        raise HTTPException(status_code=400, detail="Google did not return an email.")

    # --- Upsert: find existing user or create a new one ---
    result = await db.execute(select(Users).where(Users.email == google_email))
    user = result.scalars().first()

    if not user:
        # New user — create account with unusable password (OAuth-only)
        user = Users(
            email=google_email,
            # A placeholder hash that can never be produced by bcrypt,
            # so the user cannot log in with a password (OAuth only).
            hashed_password="!oauth_user_no_password",
            is_active=True,
        )
        db.add(user)
        await db.flush()

        profile = Profiles(
            user_id=user.id,
            first_name=google_user.get("given_name"),
            last_name=google_user.get("family_name"),
        )
        db.add(profile)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="This account has been deactivated.")

    # --- Issue our own JWTs ---
    tokens = await _issue_tokens_for_user(user, response, db)

    # Redirect the browser to the frontend with the access token as a query param.
    # The frontend reads it once and stores it in memory, then discards the URL param.
    redirect_url = (
        f"{settings.FRONTEND_URL}/auth/callback"
        f"?access_token={tokens['access_token']}"
    )
    return RedirectResponse(redirect_url, status_code=302)
