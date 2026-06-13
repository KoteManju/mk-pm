import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./project_management.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project Management API"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"

    # Email notifications and inbound replies
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    EMAIL_FROM_NAME: str = "Project Management"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    IMAP_HOST: str = ""
    IMAP_PORT: int = 993
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    IMAP_FOLDER: str = "INBOX"
    IMAP_USE_SSL: bool = True
    EMAIL_POLL_INTERVAL_SECONDS: int = 60

    UPLOAD_DIR: str = "./uploads"

settings = Settings()
