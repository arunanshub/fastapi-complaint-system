from __future__ import annotations

import typing
from functools import lru_cache
from typing import Iterable

import boto3

from ..core import settings

if typing.TYPE_CHECKING:
    from pydantic import EmailStr


class SESService:
    def __init__(self) -> None:
        self._key = settings.AWS_ACCESS_KEY
        self._secret = settings.AWS_SECRET_ACCESS_KEY
        self._ses = boto3.client(
            "ses",
            region_name=settings.AWS_SES_REGION_NAME,
            aws_access_key_id=self._key,
            aws_secret_access_key=self._secret,
        )

    def send_email(
        self,
        subject: str,
        text_data: str,
        to_addresses: list[EmailStr],
    ) -> None:
        self._ses.send_email(
            Source=settings.AWS_SES_EMAIL_SENDER,
            Destination={
                "ToAddresses": to_addresses,
                "CcAddresses": [],
                "BccAddresses": [],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Text": {
                        "Data": text_data,
                        "Charset": "UTF-8",
                    }
                },
            },
        )


@lru_cache
def _get_cached_ses_service() -> SESService:
    return SESService()


def get_ses() -> Iterable[SESService]:
    yield _get_cached_ses_service()
