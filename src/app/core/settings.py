from __future__ import annotations

from typing import Any

from pydantic import BaseSettings, Field, validator
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default=...)
    DATABASE_URL: str = Field(default=...)
    #: This URL is derived from ``DATABASE_URL`` and not from the environment.
    DATABASE_URL_WITHOUT_DRIVER: str = Field(default=None)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    API_VERSION_URL: str = "/api/v1"

    @validator("DATABASE_URL_WITHOUT_DRIVER", pre=True)
    def get_database_name_without_driver(
        cls,
        _: str,
        values: dict[str, Any],
    ) -> str:
        db_url = make_url(values["DATABASE_URL"])
        return str(db_url.set(drivername=db_url.get_backend_name()))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
