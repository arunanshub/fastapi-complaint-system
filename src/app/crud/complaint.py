from __future__ import annotations

import typing

from sqlmodel import select

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession
    from ..models.user import User

from ..exc import DoesNotExistError
from ..models.complaint import Complaint, ComplaintCreate, ComplaintUpdate
from ..models.enums import ComplaintStatus
from .base import CRUDBase


class CRUDComplaint(CRUDBase[Complaint, ComplaintCreate, ComplaintUpdate]):
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Complaint]:
        stmt = (
            select(self.model)
            .where(self.model.complainer_id == db_obj.id)
            .offset(skip)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    async def get_pending(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Complaint]:
        stmt = (
            select(self.model)
            .where(self.model.status == ComplaintStatus.PENDING)
            .offset(skip)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

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
