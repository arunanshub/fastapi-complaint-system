from __future__ import annotations

from uuid import UUID  # noqa: TC003

from sqlmodel import Field, SQLModel

from .base import Monetary, SQLBase


class TransactionBase(SQLModel):
    quote_id: UUID
    transfer_id: int
    target_account_id: int
    amount: Monetary


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(SQLModel):
    pass


class Transaction(SQLBase, TransactionBase, table=True):
    complaint_id: int = Field(default=None, foreign_key="complaint.id")
