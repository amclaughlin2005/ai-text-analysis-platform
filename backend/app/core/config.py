"""
Configuration management for the AI-Powered Text Analysis Platform
Handles environment variables, settings validation, and configuration defaults.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Configuration
    APP_NAME: str = "AI-Powered Text Analysis Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis Configuration (Celery & Caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.3
    
    # Clerk Authentication
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Security Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    UPLOAD_RATE_LIMIT: int = 10
    
    # Processing Limits
    MAX_UPLOAD_SIZE_MB: int = 100
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes
    UPLOAD_DIR: str = "uploads"
    MAX_QUESTIONS_PER_DATASET: int = 50000
    BATCH_PROCESSING_SIZE: int = 100
    MAX_CONCURRENT_JOBS: int = 5
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-domain.vercel.app"
    ]
    
    # Allowed hosts for security
    ALLOWED_HOSTS: List[str] = ["*"]  # Restrict in production
    
    # Frontend Integration
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Monitoring & Logging
    SENTRY_DSN: Optional[str] = None
    LOG_FORMAT: str = "json"
    PROMETHEUS_ENABLED: bool = False
    
    @validator('DATABASE_URL', pre=True)
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        """Build database URL if not provided directly"""
        if v:
            return v
        
        # Build from individual components if available
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'text_analysis_platform')
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @validator('CORS_ORIGINS', pre=True)
    def assemble_cors_origins(cls, v: List[str]) -> List[str]:
        """Parse CORS origins from environment if provided as string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ALLOWED_HOSTS', pre=True)
    def assemble_allowed_hosts(cls, v: List[str]) -> List[str]:
        """Parse allowed hosts from environment if provided as string"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('DEBUG', pre=True)
    def parse_debug(cls, v) -> bool:
        """Parse debug flag from various string representations"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is one of the allowed values"""
        allowed = ['development', 'testing', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Development environment defaults
class DevelopmentSettings(Settings):
    """Development-specific settings"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite:///./test_db.sqlite"  # SQLite for easy development
    
# Production environment defaults
class ProductionSettings(Settings):
    """Production-specific settings"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = []  # Must be configured in production
    JWT_SECRET_KEY: str  # Must be set in production

# Testing environment defaults
class TestingSettings(Settings):
    """Testing-specific settings"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test_db.sqlite"
    REDIS_URL: str = "redis://localhost:6379/10"  # Separate Redis DB for testing

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching
    Environment can be overridden with APP_ENV environment variable
    """
    environment = os.getenv("APP_ENV", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Create global settings instance
settings = get_settings()

# Configuration validation
def validate_required_settings():
    """Validate that all required settings are present for the current environment"""
    errors = []
    
    if settings.ENVIRONMENT == "production":
        required_settings = [
            ('DATABASE_URL', 'Database connection required'),
            ('OPENAI_API_KEY', 'OpenAI API key required for text analysis'),
            ('CLERK_SECRET_KEY', 'Clerk secret key required for authentication'),
            ('JWT_SECRET_KEY', 'JWT secret key must be set in production'),
        ]
        
        for setting_name, error_message in required_settings:
            if not getattr(settings, setting_name, None):
                errors.append(f"{setting_name}: {error_message}")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {error}" for error in errors))

# Validate on import in production
if settings.ENVIRONMENT == "production":
    try:
        validate_required_settings()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        # Don't exit here, let the app handle it gracefully
