from __future__ import annotations

import typing

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.settings import settings


def _remove_drivername_from_url(url: str) -> str:
    db_url = make_url(url)
    return str(db_url.set(drivername=db_url.get_backend_name()))


DATABASE_URL = settings.DATABASE_URL

DATABASE_URL_WITHOUT_DRIVER = _remove_drivername_from_url(
    settings.DATABASE_URL
)

engine = create_async_engine(settings.DATABASE_URL)


async def get_db() -> typing.AsyncIterable[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
