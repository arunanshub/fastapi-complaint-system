from __future__ import annotations

from fastapi import APIRouter

from . import auth, complaint, user

router = APIRouter()

router.include_router(auth.router, prefix="/login", tags=["login"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(
    complaint.router, prefix="/complaints", tags=["complaints"]
)
