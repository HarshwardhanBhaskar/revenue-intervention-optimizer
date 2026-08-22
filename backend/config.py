"""
Revenue Intervention Optimizer — Backend Configuration

Loads all configuration from environment variables.
Never hardcode secrets or credentials.
"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="Revenue Intervention Optimizer")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=False)
    app_secret_key: str = Field(default="change-me-in-production")

    # Database (defaults to local sqlite for zero-config run, override with PostgreSQL in .env)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./rio_dev.db"
    )
    database_sync_url: str = Field(
        default="sqlite:///./rio_dev.db"
    )

    # Razorpay
    razorpay_key_id: str = Field(default="rzp_test_placeholder")
    razorpay_key_secret: str = Field(default="placeholder_secret")
    razorpay_webhook_secret: str = Field(default="placeholder_webhook_secret")

    # Supabase
    supabase_url: str = Field(default="https://hctvyazovhjyajqohmto.supabase.co")
    supabase_anon_key: str = Field(default="sb_publishable_VUGUEoOapv686UqbZ6joFw_-Uoq5IaB")
    supabase_service_role_key: str = Field(default="")

    # LLM
    llm_provider: str = Field(default="gemini")
    gemini_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")

    # Auth
    jwt_secret_key: str = Field(default="change-me-jwt-secret")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_minutes: int = Field(default=60)

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60)

    # ML
    model_dir: str = Field(default="../ml/models")
    model_fallback_policy: str = Field(default="retry_once")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def model_path(self) -> Path:
        return Path(self.model_dir).resolve()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
