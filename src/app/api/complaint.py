from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from ..api.deps import get_current_complainer
from ..crud import complaint
from ..database import get_db
from ..models.complaint import Complaint, ComplaintCreate, ComplaintRead
from ..models.user import User  # noqa: TC002

router = APIRouter()


@router.get("/", response_model=list[ComplaintRead])
async def get_complaints(
    db: AsyncSession = Depends(get_db),
    db_user: User = Depends(get_current_complainer),
) -> list[Complaint]:
    return await complaint.get_by_user(db, db_obj=db_user)


@router.post(
    "/",
    response_model=ComplaintRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_complaint(
    complaint_in: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    db_user: User = Depends(get_current_complainer),
) -> Complaint:
    return await complaint.create(
        db,
        obj_in=complaint_in,
        user=db_user,
    )
