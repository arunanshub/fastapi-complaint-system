from __future__ import annotations

from typing import Any

from pydantic import BaseSettings, EmailStr, Field, HttpUrl, validator
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    #: The application secret key
    SECRET_KEY: str = Field(default=...)

    #: Access key for accessing AWS services.
    AWS_ACCESS_KEY: str = Field(default=...)

    #: The AWS secret access key used for accessing AWS services.
    AWS_SECRET_ACCESS_KEY: str = Field(default=...)

    #: name of the Amazon Web Services (AWS) S3 bucket to be used by the
    #: application
    AWS_BUCKET_NAME: str = Field(default=...)

    #: the AWS region to be used for SES.
    AWS_SES_REGION_NAME: str = Field(default=...)

    #: the SES email sender
    AWS_SES_EMAIL_SENDER: EmailStr = Field(default=...)

    #: The API endpoint of Wise
    WISE_ENDPOINT: HttpUrl = Field(default=...)

    #: Wise API token
    WISE_TOKEN: str = Field(default=...)

    #: This URL is derived from ``DATABASE_URL`` and not from the environment.
    DATABASE_URL: str = Field(default=...)

    #: a URL derived from ``DATABASE_URL`` that excludes the database driver
    #: name.
    DATABASE_URL_WITHOUT_DRIVER: str = Field(default=None)

    #: The time in minutes after which an access token will expire.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #: The URL path prefix for the API version.
    API_VERSION_URL: str = "/api/v1"

    #: The URL path prefix for the API version.
    PROJECT_NAME: str = "Complaint System"

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
