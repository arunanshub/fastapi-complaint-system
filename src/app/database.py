from __future__ import annotations

import typing

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.settings import settings

engine = create_async_engine(settings.DATABASE_URL)


async def get_db() -> typing.AsyncIterable[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
