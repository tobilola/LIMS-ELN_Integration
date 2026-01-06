"""
Application Configuration
Uses Pydantic Settings for environment variable management
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database - PostgreSQL
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://lims:password@localhost:5432/lims_eln",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    
    # Database - MongoDB
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        env="MONGODB_URL"
    )
    MONGODB_DATABASE: str = Field(default="lims_eln", env="MONGODB_DATABASE")
    
    # Cache - Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(default=900, env="REDIS_CACHE_TTL")  # 15 minutes
    
    # Message Queue - RabbitMQ
    RABBITMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672//",
        env="RABBITMQ_URL"
    )
    
    # Security
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External Systems - LIMS
    LIMS_API_URL: str = Field(
        default="https://lims.example.com/api",
        env="LIMS_API_URL"
    )
    LIMS_API_KEY: Optional[str] = Field(default=None, env="LIMS_API_KEY")
    LIMS_SYSTEM_TYPE: str = Field(default="labware", env="LIMS_SYSTEM_TYPE")
    
    # External Systems - ELN
    ELN_API_URL: str = Field(
        default="https://eln.example.com/api",
        env="ELN_API_URL"
    )
    ELN_API_KEY: Optional[str] = Field(default=None, env="ELN_API_KEY")
    ELN_SYSTEM_TYPE: str = Field(default="benchling", env="ELN_SYSTEM_TYPE")
    
    # ML Models
    MODEL_PATH: str = Field(default="app/ml/models", env="MODEL_PATH")
    ANOMALY_THRESHOLD: float = Field(default=0.15, env="ANOMALY_THRESHOLD")
    ML_BATCH_SIZE: int = Field(default=32, env="ML_BATCH_SIZE")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Sync Configuration
    SYNC_BATCH_SIZE: int = Field(default=100, env="SYNC_BATCH_SIZE")
    SYNC_RETRY_ATTEMPTS: int = Field(default=3, env="SYNC_RETRY_ATTEMPTS")
    SYNC_RETRY_DELAY: int = Field(default=5, env="SYNC_RETRY_DELAY")  # seconds
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Helper function to get settings
def get_settings() -> Settings:
    """Dependency injection for settings"""
    return settings
