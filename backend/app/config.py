"""Configuration management using pydantic-settings."""
from enum import Enum
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class PlanEnum(str, Enum):
    """User subscription plans."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/sourcelens",
        description="PostgreSQL database URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for Celery"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT signing"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = Field(
        default="",
        description="Cloudinary cloud name"
    )
    CLOUDINARY_API_KEY: str = Field(
        default="",
        description="Cloudinary API key"
    )
    CLOUDINARY_API_SECRET: str = Field(
        default="",
        description="Cloudinary API secret"
    )
    
    # OpenAI
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for GPT-4o Vision and embeddings"
    )
    
    # CORS
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Plan Limits
    FREE_PLAN_SEARCHES_PER_MONTH: int = 5
    
    # Image Upload
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    IMAGE_EXPIRY_DAYS: int = 30
    
    # Supplier Matching
    MIN_CONFIDENCE_THRESHOLD: float = 0.70
    EMBEDDING_DIMENSION: int = 1536
    TOP_SUPPLIERS_LIMIT: int = 20
    INITIAL_CANDIDATES_LIMIT: int = 50
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
