from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from ..core import security, settings
from ..crud import user as user_crud
from ..database import get_db
from ..models.enums import Role
from ..models.user import User  # noqa: TC002

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_VERSION_URL}/login/token"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    access_token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get the current active user using the token data.

    Args:
        db: An async session object.
        access_token: A JWT token as a string.

    Returns:
        The user from the database.

    Raises:
        HTTPException: Raised if token is invalid or the user is not found.
    """
    try:
        token_data = security.verify_access_token(access_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = await user_crud.get(db, id=token_data.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def get_current_complainer(
    user: User = Depends(get_current_user),
) -> User:
    if user.role == Role.COMPLAINER:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have enough privileges",
    )


async def get_current_approver(user: User = Depends(get_current_user)) -> User:
    if user.role == Role.APPROVER:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have enough privileges",
    )


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role == Role.ADMIN:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have enough privileges",
    )
