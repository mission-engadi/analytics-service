"""Application configuration using Pydantic settings.

Configuration is loaded from environment variables or .env file.
Different configurations can be used for dev/staging/prod environments.
"""

import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden via environment variables.
    For example, DATABASE_URL can be set in the environment or .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    PROJECT_NAME: str = "Analytics Service"
    PROJECT_DESCRIPTION: str = "Analytics and reporting service for Mission Engadi platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8009
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Override in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://engadi.org",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/analytics_service_db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (for caching, sessions, etc.)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka (for event-driven architecture)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "analytics_service"
    
    # External Services - Microservices Integration
    AUTH_SERVICE_URL: str = "http://localhost:8002"
    CONTENT_SERVICE_URL: str = "http://localhost:8003"
    PARTNERS_CRM_SERVICE_URL: str = "http://localhost:8005"
    PROJECTS_SERVICE_URL: str = "http://localhost:8006"
    SOCIAL_MEDIA_SERVICE_URL: str = "http://localhost:8007"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8008"
    
    # Data Synchronization Settings
    SYNC_ENABLED: bool = True
    SYNC_INTERVAL_MINUTES: int = 60  # Default sync every hour
    SYNC_BATCH_SIZE: int = 1000  # Number of records per batch
    SYNC_TIMEOUT_SECONDS: int = 300  # 5 minutes timeout
    SYNC_MAX_RETRIES: int = 3
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600  # 1 hour default TTL
    CACHE_METRICS_TTL_SECONDS: int = 300  # 5 minutes for metrics
    CACHE_DASHBOARD_TTL_SECONDS: int = 600  # 10 minutes for dashboards
    
    # Analytics Settings
    ANALYTICS_RETENTION_DAYS: int = 1095  # 3 years
    ANALYTICS_AGGREGATION_LEVELS: List[str] = ["hourly", "daily", "weekly", "monthly"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Monitoring
    DATADOG_API_KEY: Optional[str] = None
    DATADOG_APP_KEY: Optional[str] = None
    
    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    

# Create global settings instance
settings = Settings()
