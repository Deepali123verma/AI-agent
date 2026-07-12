"""
FastAPI Application Entry Point
Main application factory and configuration
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import chat


# Settings instance
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    Handles startup and shutdown events
    """
    # Startup
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    yield
    # Shutdown
    print(f"🛑 {settings.APP_NAME} shutting down...")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI: Configured application instance
    """
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend API for the Personal AI Agent",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Register routers
    app.include_router(chat.router)

    # Health Check Endpoint
    @app.get("/status", tags=["System"])
    async def status_check():
        """
        Status check endpoint for monitoring
        
        Returns:
            dict: Status of the application
        """
        return {
            "status": "online",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    # Root Endpoint
    @app.get("/", tags=["General"])
    async def root():
        """
        Root endpoint - API information
        
        Returns:
            dict: Welcome message and API information
        """
        return {
            "message": "Personal AI Agent Backend Running",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # Global Exception Handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Handle HTTP exceptions with consistent format"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )

    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
