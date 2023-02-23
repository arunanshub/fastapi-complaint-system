from __future__ import annotations

import os
import typing
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.concurrency import run_in_threadpool
from pyfa_converter import FormDepends  # type: ignore[import]
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from ..api.deps import (
    get_current_admin,
    get_current_approver,
    get_current_complainer,
    get_current_user,
)
from ..crud import complaint, user
from ..database import get_db
from ..exc import DoesNotExistError
from ..models.complaint import (
    Complaint,
    ComplaintCreate,
    ComplaintCreateUser,
    ComplaintRead,
)
from ..models.enums import ComplaintStatus, Role
from ..models.user import User  # noqa: TC002
from ..services.s3 import S3Service, get_s3
from ..services.ses import SESService, get_ses

if typing.TYPE_CHECKING:
    from pydantic import HttpUrl

router = APIRouter()


@router.get("/", response_model=list[ComplaintRead])
async def get_complaints(
    complaint_status: ComplaintStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    db_user: User = Depends(get_current_user),
) -> list[Complaint]:
    query = complaint.query(db).limit(limit).skip(skip)
    if complaint_status is not None:
        query = query.filter_by_status(complaint_status)
    if db_user.role in [Role.APPROVER, Role.ADMIN]:
        return await query.all()
    return await query.filter_by_user(db_user).all()


@router.post(
    "/",
    response_model=ComplaintRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_complaint(
    photo: UploadFile,
    complaint_in: ComplaintCreateUser = FormDepends(ComplaintCreateUser),
    s3_client: S3Service = Depends(get_s3),
    db: AsyncSession = Depends(get_db),
    db_user: User = Depends(get_current_complainer),
) -> Complaint:
    # check if uploaded file is valid
    assert photo.filename is not None
    if photo.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            detail=f"Invalid file type: {photo.content_type}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # generate filename, upload photo and generate photo url
    extension = os.path.splitext(photo.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    await run_in_threadpool(
        s3_client.upload_fileobj,
        photo.file,
        filename,
        photo.content_type,
    )
    photo_url = typing.cast("HttpUrl", s3_client.get_object_url(filename))

    # store the generated url in the database
    complaint_data = ComplaintCreate(
        **complaint_in.dict(),
        photo_url=photo_url,
    )
    return await complaint.create(db, obj_in=complaint_data, user=db_user)


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
    response_model=None,
)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await complaint.delete(db, id=complaint_id)
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
    ses_client: SESService = Depends(get_ses),
) -> Complaint:
    try:
        db_complaint = await complaint.change_status_by_id(
            db,
            id=complaint_id,
            status=ComplaintStatus.APPROVED,
        )
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint does not exist",
        ) from e

    db_user = await user.get(db, id=db_complaint.complainer_id)
    assert db_user is not None  # TODO: what if user is deleted?
    assert db_user.email is not None

    await run_in_threadpool(
        ses_client.send_email,
        "Complaint approved!",
        "Your claim has been approved!",
        [db_user.email],
    )

    return db_complaint


@router.put(
    "/{complaint_id}/reject",
    dependencies=[Depends(get_current_approver)],
    response_model=ComplaintRead,
)
async def reject_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    ses_client: SESService = Depends(get_ses),
) -> Complaint:
    try:
        db_complaint = await complaint.change_status_by_id(
            db,
            id=complaint_id,
            status=ComplaintStatus.REJECTED,
        )
    except DoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint does not exist",
        ) from e

    db_user = await user.get(db, id=db_complaint.complainer_id)
    assert db_user is not None  # TODO: what if user is deleted?
    assert db_user.email is not None

    await run_in_threadpool(
        ses_client.send_email,
        "Complaint approved!",
        "Your claim has been rejected!",
        [db_user.email],
    )

    return db_complaint
