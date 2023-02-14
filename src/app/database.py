from __future__ import annotations

import typing

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .core import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


async def get_db() -> typing.AsyncIterable[AsyncSession]:
    """A convenience function to create one time database session.

    It is generally used with ``fastapi.Depends`` object.

    Returns:
        Asynchronous iterable with a single asynchronous session.
    """
    async with AsyncSession(engine) as session:
        yield session
