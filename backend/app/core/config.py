import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./project_management.db"  # Changed to SQLite for testing
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project Management API"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]  # Allow all origins for development
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()