"""
Base class for performing CRUD (Create, Read, Update, Delete) operations on a
database.
"""
from __future__ import annotations

import typing
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from ..exc import DoesNotExistError, NotUniqueError
from ..models.base import SQLBase

if typing.TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


ModelType = TypeVar("ModelType", bound=SQLBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)
_T = TypeVar("_T", bound="CRUDBaseQueryBuilder")


class CRUDBaseQueryBuilder(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.db = db
        self.model = model
        self.query = select(self.model).order_by(self.model.id)

    def skip(self: _T, skip: int) -> _T:
        assert self.model.id is not None
        self.query = self.query.where(self.model.id > skip)
        return self

    def limit(self: _T, limit: int) -> _T:
        self.query = self.query.limit(limit)
        return self

    async def all(self) -> list[ModelType]:
        return (await self.db.execute(self.query)).scalars().all()

    async def first(self) -> ModelType | None:
        return (await self.db.execute(self.query.limit(1))).scalar()

    async def one(self) -> ModelType:
        return (await self.db.execute(self.query)).scalar_one()

    async def one_or_none(self) -> ModelType | None:
        return (await self.db.execute(self.query)).scalar_one_or_none()


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    The CRUDBase class provides a base implementation for Create, Read, Update,
    and Delete (CRUD) operations for a database model.

    The class is parameterized with three types: ModelType, CreateSchemaType,
    and UpdateSchemaType. The ModelType is the database model class, the
    CreateSchemaType is the schema for the create operation, and the
    UpdateSchemaType is the schema for the update operation.
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    def query(self, db: AsyncSession) -> CRUDBaseQueryBuilder[ModelType]:
        return CRUDBaseQueryBuilder(self.model, db)

    async def get(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """Retrieves a single record from the database.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            id: The unique identifier/primary key for the record.

        Returns:
            A single record or ``None`` if the record is not found.
        """
        return await db.get(self.model, id)

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        **kwargs: SQLModel,
    ) -> ModelType:
        """Creates a new record in the database.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            obj_in:
                Data for the new record that will be inserted into the
                database.
            kwargs:
                Additional attributes controlled by foreign keys in
                relationships to be set on the new database object beyond those
                specified in ``obj_in``.

        Returns:
            The created database object.
        """
        db_obj = self.model.from_orm(obj_in)
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        return await self.add_record(db, db_obj=db_obj)

    async def add_record(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> ModelType:
        """Adds a new record in the database and checks for integrity issues.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            db_obj:
                Data for the new record that will be inserted into the
                database.

        Returns:
            The created database object.

        Raises:
            NotUniqueError: If the record already exists in database.
        """
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise NotUniqueError("field(s) must be unique") from e
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Updates an existing record in the database.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            db_obj: Database record that will be updated.
            obj_in:
                New data that will be used to update the existing database
                record.

        Returns:
            The created database object.
        """
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        return await self.add_record(db, db_obj=db_obj)

    async def delete(self, db: AsyncSession, *, id: int) -> None:
        """Deletes a record from the database based on the given id.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            id: The unique identifier/primary key for the record.

        Raises:
            DoesNotExistError: Raised if the record does not exist.
        """
        obj = await db.get(self.model, id)
        if obj is None:
            raise DoesNotExistError("the record does not exist")
        await db.delete(obj)
        await db.commit()
