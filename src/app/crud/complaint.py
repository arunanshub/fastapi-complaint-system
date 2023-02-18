from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession
    from ..models.user import User
    from ..models.enums import ComplaintStatus

from ..exc import DoesNotExistError
from ..models.complaint import Complaint, ComplaintCreate, ComplaintUpdate
from .base import CRUDBase, CRUDBaseQueryBuilder


class ComplaintQueryBuilder(CRUDBaseQueryBuilder[Complaint]):
    def filter_by_user(self, user: User) -> ComplaintQueryBuilder:
        self.query = self.query.where(self.model.complainer_id == user.id)
        return self

    def filter_by_status(
        self, status: ComplaintStatus
    ) -> ComplaintQueryBuilder:
        self.query = self.query.where(self.model.status == status)
        return self


class CRUDComplaint(CRUDBase[Complaint, ComplaintCreate, ComplaintUpdate]):
    def query(self, db: AsyncSession) -> ComplaintQueryBuilder:
        return ComplaintQueryBuilder(self.model, db)

    async def get_by_id(
        self, db: AsyncSession, *, id: int
    ) -> Complaint | None:
        return await self.get(db, id=id)

    async def change_status_by_id(
        self,
        db: AsyncSession,
        *,
        id: int,
        status: ComplaintStatus,
    ) -> Complaint:
        db_complaint = await self.get(db, id=id)
        if db_complaint is None:
            raise DoesNotExistError("complaint does not exist")
        complaint_in = ComplaintUpdate(status=status)
        return await self.update(db, db_obj=db_complaint, obj_in=complaint_in)


complaint = CRUDComplaint(Complaint)
