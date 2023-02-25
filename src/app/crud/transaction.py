from __future__ import annotations

import typing

from ..models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
)
from .base import CRUDBase

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


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
