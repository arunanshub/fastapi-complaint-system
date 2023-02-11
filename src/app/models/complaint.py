# isort: dont-add-imports

from datetime import datetime  # noqa: TC003

from pydantic import HttpUrl  # noqa: TC002
from sqlmodel import Column, Field, SQLModel, Text, func

from .enums import ComplaintStatus


class ComplaintBase(SQLModel):
    title: str = Field(max_length=120)
    description: str = Field(sa_column=Column(Text(), nullable=False))
    photo_url: HttpUrl
    amount: float
    created_at: datetime = Field(
        sa_column_kwargs={
            "server_default": func.now(),
        }
    )
    status: ComplaintStatus = Field(
        sa_column_kwargs={
            "server_default": ComplaintStatus.PENDING.name,
        }
    )


class Complaint(ComplaintBase, table=True):  # type: ignore[call-arg]
    id: int | None = Field(default=None, primary_key=True)
    complainer_id: int = Field(default=None, foreign_key="user.id")
