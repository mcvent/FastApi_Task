from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional
import os
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""

    # Приложение
    APP_NAME: str = Field(default="FastAPI Blog API", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # База данных
    # DATABASE_URL: str = Field(
    #     default="postgres:///./db.sqlite3",
    #     env="DATABASE_URL"
    # )

    POSTGRES_SCHEMA: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_RECONNECT_INTERVAL_SEC: int

    @property
    def postgres_url(self) -> str:
        creds = f"{self.POSTGRES_USER.get_secret_value()}:{self.POSTGRES_PASSWORD.get_secret_value()}"
        return f"postgresql+asyncpg://{creds}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Безопасность
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    LOG_FILE: str = Field(default="app.log", env="LOG_FILE")
    LOG_LEVEL: str = Field(default="ERROR", env="LOG_LEVEL")

    # # Пути
    # BASE_DIR: str = Field(default=str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), env="BASE_DIR")

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_log_level(self) -> int:
        """Преобразует строковый уровень логирования в int"""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(self.LOG_LEVEL.upper(), logging.ERROR)


settings = Settings()
