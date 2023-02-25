from __future__ import annotations

import typing

from pydantic import condecimal
from sqlmodel import Field, SQLModel


class SQLBase(SQLModel):
    """
    The base class for all **SQL** models. It contains only one field: the
    ``id``, which is the primary key.
    """

    id: int | None = Field(default=None, primary_key=True)


if typing.TYPE_CHECKING:
    from decimal import Decimal

    class Monetary(Decimal):
        """Type representing monetary value."""

else:
    Monetary = condecimal(ge=0, max_digits=19, decimal_places=4)
