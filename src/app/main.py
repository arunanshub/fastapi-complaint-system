from __future__ import annotations

from fastapi import FastAPI

from .api import router
from .core import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(router, prefix=settings.API_VERSION_URL)
