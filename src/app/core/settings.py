from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = ""
    DATABASE_URL: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
