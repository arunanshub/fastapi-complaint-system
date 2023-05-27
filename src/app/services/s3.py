from __future__ import annotations

from functools import lru_cache
from typing import IO, AsyncIterable

import boto3
from botocore.exceptions import ClientError
from fastapi.concurrency import run_in_threadpool

from .. import exc
from ..core import settings


class S3Service:
    def __init__(self) -> None:
        self._key = settings.AWS_ACCESS_KEY
        self._secret = settings.AWS_SECRET_ACCESS_KEY
        self._bucket = settings.AWS_BUCKET_NAME
        self._s3 = boto3.client(
            "s3",
            aws_access_key_id=self._key,
            aws_secret_access_key=self._secret,
        )

    async def upload_fileobj(
        self,
        fileobj: IO[bytes],
        key: str,
        content_type: str,
    ) -> None:
        try:
            await run_in_threadpool(
                self._s3.upload_fileobj,
                fileobj,
                self._bucket,
                key,
                ExtraArgs={"ACL": "public-read", "ContentType": content_type},
            )
        except ClientError as e:
            msg = "failed to upload file object"
            raise exc.UploadFailedError(msg) from e

    def get_object_url(self, key: str) -> str:
        return f"https://{self._bucket}.s3.amazonaws.com/{key}"


@lru_cache
def _get_cached_s3_service() -> S3Service:
    return S3Service()


async def get_s3() -> AsyncIterable[S3Service]:
    yield _get_cached_s3_service()
