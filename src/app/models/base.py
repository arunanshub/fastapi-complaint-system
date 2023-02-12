from __future__ import annotations

from sqlmodel import Field, SQLModel


class SQLBase(SQLModel):
    """
    The base class for all **SQL** models. It contains only one field: the
    ``id``, which is the primary key.
    """

    id: int | None = Field(default=None, primary_key=True)
