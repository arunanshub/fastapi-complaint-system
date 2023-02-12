from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from ..core import security
from ..crud import user
from ..database import get_db
from ..models.token import Token

router = APIRouter()


@router.post("/token")
async def login_for_token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    db_user = await user.authenticate(
        db,
        email=EmailStr(form.username),
        password=form.password,
    )
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=security.create_access_token(db_user.id),
        token_type="Bearer",
    )
