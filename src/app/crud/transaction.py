from __future__ import annotations

import typing

from ..models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
)
from .base import BaseQueryBuilder, CRUDBase

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

T = typing.TypeVar("T", bound="TransactionQueryBuilder")


class TransactionQueryBuilder(BaseQueryBuilder[Transaction]):
    def filter_by_complaint_id(self: T, complaint_id: int) -> T:
        self.query = self.query.where(self.model.complaint_id == complaint_id)
        return self


class CRUDTransaction(
    CRUDBase[Transaction, TransactionCreate, TransactionUpdate]
):
    # FIXME: better to use command pattern here
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
        obj_in: TransactionUpdate,
    ) -> Transaction:
        del db, db_obj, obj_in
        raise NotImplementedError("Cannot update a transaction")

    def query(self, db: AsyncSession) -> TransactionQueryBuilder:
        return TransactionQueryBuilder(self.model, db)


transaction = CRUDTransaction(Transaction)
