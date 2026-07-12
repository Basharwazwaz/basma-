import logging
import json
import secrets
from typing import List, Union, Optional

from pydantic import PostgresDsn, computed_field, field_validator, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "super_secret_key_change_in_production"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Basma+ API"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "basma_db"
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=5432,
            path=self.POSTGRES_DB,
        )

    # JWT Settings
    SECRET_KEY: str = _DEFAULT_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:8080"

    # AI Settings
    GEMINI_API_KEY: str = ""

    # Mail Settings (optional)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@basmaplus.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.dummy.com"

    @model_validator(mode="after")
    def _validate_secret_key(self):
        if self.SECRET_KEY == _DEFAULT_SECRET:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "SECRET_KEY must be changed from the default in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            # Auto-generate a random key for development
            self.SECRET_KEY = secrets.token_hex(32)
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
