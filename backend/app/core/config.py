"""
Core Configuration Module
Contains application-wide settings and configuration
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application Settings
    Loads configuration from environment variables with defaults
    """

    # Application
    APP_NAME: str = "Personal AI Agent Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Frontend dev server (Vite)
        "http://localhost:3000",  # React dev server
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Environment
    ENVIRONMENT: str = "development"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # Google Gemini Configuration
    GEMINI_API_KEY: Optional[str] = None
    # Using gemini-3-flash-preview (same as Google AI Studio)
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached)
    Cache ensures settings are loaded only once
    """
    return Settings()
