from __future__ import annotations

import typing

from decouple import config
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


def _remove_drivername_from_url(url: str) -> str:
    db_url = make_url(url)
    return str(db_url.set(drivername=db_url.get_backend_name()))


DATABASE_URL = typing.cast("str", config("DATABASE_URL", cast=str))

DATABASE_URL_WITHOUT_DRIVER = _remove_drivername_from_url(DATABASE_URL)

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine = create_async_engine(DATABASE_URL)


async def get_db() -> typing.AsyncIterable[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
