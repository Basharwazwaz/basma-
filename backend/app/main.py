from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_router

# Setup structured logging
logger = setup_logging(debug=settings.DEBUG)

def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Set up CORS middleware - Must be first middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )

    # Set up global exception handlers
    setup_exception_handlers(app)

    # Add OPTIONS handler for CORS preflight requests
    @app.options("/{path:path}")
    async def preflight_handler(path: str):
        """Handle CORS preflight requests."""
        return None

    # Include the main API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/")
    def root():
        """Root endpoint that redirects to docs."""
        return {"message": "Welcome to the Basma+ API. Visit /api/v1/docs for documentation."}

    logger.info("FastAPI application created and configured.")
    return app

app = create_app()
