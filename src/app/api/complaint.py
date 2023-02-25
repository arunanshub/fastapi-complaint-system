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
from pyfa_converter import FormDepends  # type: ignore[import]
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: TC002

from app import exc

from ..api.deps import (
    get_current_admin,
    get_current_approver,
    get_current_complainer,
    get_current_user,
)
from ..crud import complaint, transaction, user
from ..database import get_db
from ..exc import DoesNotExistError
from ..models.complaint import (
    Complaint,
    ComplaintCreate,
    ComplaintCreateUser,
    ComplaintRead,
)
from ..models.enums import ComplaintStatus, Role
from ..models.transaction import TransactionCreate
from ..models.user import User  # noqa: TC002
from ..services.s3 import S3Service, get_s3
from ..services.ses import SESService, get_ses
from ..services.wise import WiseService, get_wise

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
    wise_client: WiseService = Depends(get_wise),
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
    await s3_client.upload_fileobj(photo.file, filename, photo.content_type)
    photo_url = typing.cast("HttpUrl", s3_client.get_object_url(filename))

    # store the generated url in the database
    complaint_data = ComplaintCreate(
        **complaint_in.dict(),
        photo_url=photo_url,
    )
    db_complaint = await complaint.create(
        db, obj_in=complaint_data, user=db_user
    )
    await db.refresh(db_user)

    # create a transaction
    assert db_user.iban is not None
    wise_transaction = await wise_client.issue_transaction(
        f"{db_user.first_name} {db_user.last_name}",
        db_user.iban,
        db_complaint.amount,
    )
    assert db_complaint.id is not None
    transaction_in = TransactionCreate(
        **wise_transaction.dict(),
        complaint_id=db_complaint.id,
    )
    await transaction.create(db, obj_in=transaction_in)
    await db.refresh(db_complaint)
    return db_complaint


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
    wise_client: WiseService = Depends(get_wise),
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

    # fund the transfer created in create_complaint
    assert db_complaint.id is not None
    db_transaction = (
        await transaction.query(db)
        .filter_by_complaint_id(db_complaint.id)
        .one()
    )
    try:
        await wise_client.fund_transfer(db_transaction.transfer_id)
    except exc.FailedTransactionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The transaction has already been approved",
        )

    # notify user about the transfer
    db_user = await user.get(db, id=db_complaint.complainer_id)
    assert db_user is not None  # TODO: what if user is deleted?
    assert db_user.email is not None
    await ses_client.send_email(
        "Complaint approved!", "Your claim has been approved!", [db_user.email]
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
    wise_client: WiseService = Depends(get_wise),
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

    assert db_complaint.id is not None
    db_transaction = (
        await transaction.query(db)
        .filter_by_complaint_id(db_complaint.id)
        .one()
    )

    try:
        await wise_client.cancel_transfer(db_transaction.transfer_id)
    except exc.CancelledTransactionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint has already been cancelled",
        )

    db_user = await user.get(db, id=db_complaint.complainer_id)
    assert db_user is not None  # TODO: what if user is deleted?
    assert db_user.email is not None
    await ses_client.send_email(
        "Complaint rejected!", "Your claim has been rejected!", [db_user.email]
    )

    return db_complaint
