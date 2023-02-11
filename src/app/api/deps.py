from __future__ import annotations

import typing

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

from ..core import security
from ..core.settings import settings
from ..database import get_db
from ..models.user import User

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
        access_token: A jwt token as a string.

    Returns:
        The user from the database.

    Raises:
        HTTPException: Raised if token is invalid or the user is not found.
    """
    token_data = security.verify_access_token(access_token)
    user = await db.get(User, token_data.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
