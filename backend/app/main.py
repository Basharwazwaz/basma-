from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import SecurityHeadersMiddleware
from app.api.v1.router import api_router
import os

# Setup structured logging
logger = setup_logging(debug=settings.DEBUG)

def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application.
    """
    is_production = settings.ENVIRONMENT == "production"

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if not is_production else None,
        docs_url=f"{settings.API_V1_STR}/docs" if not is_production else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if not is_production else None,
    )

    # Rate limiter state + middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    # Set up CORS middleware - Must be first middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        max_age=3600,
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Set up global exception handlers
    setup_exception_handlers(app)

    # Include the main API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Serve uploaded files (avatars, etc.)
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    if os.path.isdir(uploads_dir):
        app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    @app.get("/")
    def root():
        """Root endpoint that redirects to docs."""
        return {"message": "Welcome to the Basma+ API."}

    logger.info("FastAPI application created and configured.")
    return app


async def _rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

app = create_app()
