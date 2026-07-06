from fastapi import APIRouter
from app.api.v1 import auth, user, profile, productivity, health, gamification, notifications, dashboard

api_router = APIRouter()
api_router.include_router(auth.router,    prefix="/auth",    tags=["Authentication"])
api_router.include_router(user.router,    prefix="/user",    tags=["User"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(productivity.router, prefix="/productivity", tags=["Productivity"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
@api_router.get("/health")
def health_check():
    """
    Health check endpoint to verify backend is up.
    """
    return {"status": "ok", "service": "Basma+ API"}
