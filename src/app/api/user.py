from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002
from starlette import status

from ..api.deps import get_current_user
from ..crud import user
from ..database import get_db
from ..exc import NotUniqueError
from ..models.user import User, UserCreate, UserRead

router = APIRouter()


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        return await user.create(db, obj_in=user_in)
    except NotUniqueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from e
