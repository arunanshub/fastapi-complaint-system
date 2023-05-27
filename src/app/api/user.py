from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr  # noqa: TC002
from starlette import status
from typing_extensions import Annotated

from ..api.deps import get_current_admin, get_current_user
from ..crud import user
from ..database import Database
from ..exc import DoesNotExistError, NotUniqueError
from ..models.enums import Role
from ..models.user import User, UserCreate, UserRead, UserUpdate

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(get_current_admin)],
)
async def get_users(
    db: Database,
    skip: Annotated[int, Query(0, ge=0)],
    limit: Annotated[int, Query(100, ge=0, le=100)],
    email: EmailStr | None = None,
) -> list[User]:
    if email is None:
        return await user.query(db).limit(limit).skip(skip).all()
    db_user = await user.query(db).filter_by_email(email).one_or_none()
    return [db_user] if db_user else []


@router.patch("/", response_model=UserRead)
async def update_user(
    user_in: UserUpdate,
    db_user: CurrentUser,
    db: Database,
) -> User:
    return await user.update(db, db_obj=db_user, obj_in=user_in)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: Database) -> User:
    try:
        return await user.create(db, obj_in=user_in)
    except NotUniqueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from e


@router.put(
    "/{user_id}/make-admin",
    response_model=UserRead,
    dependencies=[Depends(get_current_admin)],
)
async def make_admin(user_id: int, db: Database) -> User:
    try:
        return await user.change_role_by_id(db, id=user_id, role=Role.ADMIN)
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        ) from e


@router.put(
    "/{user_id}/make-approver",
    response_model=UserRead,
    dependencies=[Depends(get_current_admin)],
)
async def make_approver(user_id: int, db: Database) -> User:
    try:
        return await user.change_role_by_id(db, id=user_id, role=Role.APPROVER)
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        ) from e
