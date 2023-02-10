from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default=...)
    DATABASE_URL: str = Field(default=...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
