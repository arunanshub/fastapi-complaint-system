from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import text

from .api import router
from .core import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(router, prefix=settings.API_VERSION_URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_services() -> None:
    from .database import get_db
    from .services import s3, ses, wise

    async for db in get_db():
        await db.execute(text("SELECT 1;"))

    async for _ in wise.get_wise():
        pass
    async for _ in ses.get_ses():
        pass
    async for _ in s3.get_s3():
        pass
