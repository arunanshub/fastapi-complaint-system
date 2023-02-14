from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from ..api.deps import (
    get_current_admin,
    get_current_approver,
    get_current_complainer,
)
from ..crud import complaint
from ..database import get_db
from ..exc import DoesNotExistError
from ..models.complaint import Complaint, ComplaintCreate, ComplaintRead
from ..models.enums import ComplaintStatus
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


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
):  # noqa: ANN201
    try:
        return await complaint.delete(db, id=complaint_id)
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint does not exist",
        ) from e


@router.put(
    "/{complaint_id}/approve",
    dependencies=[Depends(get_current_approver)],
    response_model=ComplaintRead,
)
async def approve_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
) -> Complaint:
    try:
        return await complaint.change_status_by_id(
            db,
            id=complaint_id,
            status=ComplaintStatus.APPROVED,
        )
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint does not exist",
        ) from e


@router.put(
    "/{complaint_id}/reject",
    dependencies=[Depends(get_current_approver)],
    response_model=ComplaintRead,
)
async def reject_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
) -> Complaint:
    try:
        return await complaint.change_status_by_id(
            db,
            id=complaint_id,
            status=ComplaintStatus.REJECTED,
        )
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint does not exist",
        ) from e
