"""
三国演义 · 全球三市数据可视化系统
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- App ---
    APP_NAME: str = "三国演义 · 全球三市数据可视化系统"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    DATABASE_URL: str = "postgresql://stockuser:stockpass@localhost:5432/stockdb"
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- JWT ---
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # --- Email (QQ Mail) ---
    QQ_EMAIL_SENDER: str = ""
    QQ_EMAIL_AUTH_CODE: str = ""
    QQ_SMTP_SERVER: str = "smtp.qq.com"
    QQ_SMTP_PORT: int = 587

    # --- API Keys ---
    FINNHUB_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""
    FMP_API_KEY: str = ""
    FRED_API_KEY: str = ""

    # --- Scheduler ---
    SCHEDULER_ENABLED: bool = True
    MARKET_CLOSE_HOUR: int = 15
    DAILY_REPORT_HOUR: int = 16
    ALERT_CHECK_INTERVAL: int = 30  # minutes

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
