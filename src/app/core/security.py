from __future__ import annotations

from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import ValidationError

from ..models import token
from .settings import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create an access token using the subject and expiry time-delta.

    Args:
        subject: Data that goes in JWT's ``sub`` field.
        expires_delta: When should the JWT token expire.

    Returns:
        A token as a string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(access_token: str) -> token.TokenPayload:
    """Validate the access token and return the token payload.

    Args:
        access_token: The access token as a string.

    Returns:
        A token payload containing the data.

    Raises:
        HTTPException: Raised if the token or token data is invalid.
    """
    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = token.TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    return token_data


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against a given hash.

    Args:
        plain_password: The password to verify.
        hashed_password: The hash of the password.

    Returns:
        True if password is valid, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash from given password.

    Args:
        password: A password as a string.

    Returns:
        Hash of the password as string.
    """
    return pwd_context.hash(password)
