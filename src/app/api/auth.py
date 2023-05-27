from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from typing_extensions import Annotated

from ..core import security
from ..crud import user
from ..database import Database
from ..models.token import Token

router = APIRouter()


@router.post("/token")
async def login_for_token(
    db: Database,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
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
