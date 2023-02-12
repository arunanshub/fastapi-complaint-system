from __future__ import annotations

from fastapi import APIRouter

from . import auth, user

router = APIRouter()

router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/login", tags=["login"])
