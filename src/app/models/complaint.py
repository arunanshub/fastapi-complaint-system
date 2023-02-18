# isort: dont-add-imports

from datetime import datetime  # noqa: TC003
from typing import Optional

from pydantic import HttpUrl  # noqa: TC002
from sqlmodel import Column, Field, Relationship, SQLModel, Text, func

from .base import SQLBase
from .enums import ComplaintStatus


class ComplaintBase(SQLModel):
    title: str = Field(max_length=120)
    description: str = Field(sa_column=Column(Text(), nullable=False))
    photo_url: HttpUrl
    amount: float
    created_at: datetime | None = Field(
        nullable=False,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    status: ComplaintStatus | None = Field(
        nullable=False,
        sa_column_kwargs={
            "server_default": ComplaintStatus.PENDING.name,
        },
    )


class ComplaintCreate(SQLModel):
    title: str = Field(max_length=120)
    description: str
    photo_url: HttpUrl
    amount: float


class ComplaintUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=120)
    description: str | None = None
    photo_url: HttpUrl | None = None
    amount: float | None = None
    status: ComplaintStatus | None = None


class ComplaintRead(SQLModel):
    id: int
    title: str
    description: str
    photo_url: HttpUrl
    amount: float
    created_at: datetime
    status: ComplaintStatus


class ComplaintReadWithUser(ComplaintRead):
    user: Optional["UserRead"]


class Complaint(SQLBase, ComplaintBase, table=True):  # type: ignore[call-arg]
    complainer_id: int = Field(default=None, foreign_key="user.id", index=True)
    user: Optional["User"] = Relationship(
        back_populates="complaints",
        sa_relationship_kwargs={"lazy": "raise"},
    )


from .user import User, UserRead  # noqa: E402,TC002

ComplaintReadWithUser.update_forward_refs(UserRead=UserRead)
