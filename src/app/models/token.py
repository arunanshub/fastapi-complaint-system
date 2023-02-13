from __future__ import annotations

from sqlmodel import SQLModel


class Token(SQLModel):
    """Represents a token as sent to the user."""

    access_token: str
    token_type: str


class TokenPayload(SQLModel):
    """The token contents."""

    sub: int
