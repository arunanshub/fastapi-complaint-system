"""Module for User CRUD operations."""
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from pydantic import EmailStr
    from sqlmodel.ext.asyncio.session import AsyncSession
    from sqlmodel import SQLModel
    from ..models.enums import Role

from ..core import security
from ..exc import DoesNotExistError
from ..models.user import User, UserCreate, UserUpdate
from .base import CRUDBase, CRUDBaseQueryBuilder


class UserQueryBuilder(CRUDBaseQueryBuilder[User]):
    def filter_by_email(self, email: EmailStr) -> UserQueryBuilder:
        self.query = self.query.where(self.model.email == email)
        return self


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    This class is a subclass of ``CRUDBase`` that is specific to the ``User``
    model. It extends the base class to provide additional methods specific to
    the User model.
    """

    def query(self, db: AsyncSession) -> UserQueryBuilder:
        return UserQueryBuilder(self.model, db)

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate,
        **kwargs: SQLModel,
    ) -> User:
        """Creates a new user in the database.

        Before ading the user in the database, the user's password is hashed.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            obj_in:
                Data for the new user that will be inserted into the database.
            kwargs:
                Additional attributes controlled by foreign keys in
                relationships to be set on the new database object beyond those
                specified in ``obj_in``.

        Returns:
            The created database object.
        """
        obj_in.password = security.get_password_hash(obj_in.password)
        return await super().create(db, obj_in=obj_in, **kwargs)

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate,
    ) -> User:
        """Update existing user in the database.

        Before updating the user information in the database, the method checks
        if a new password has been provided in ``obj_in``, and if so, it hashes
        the password.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            db_obj: The user object that needs to be updated in the database.
            obj_in: The updated user information.

        Returns:
            Returns the updated user.
        """
        if obj_in.password is not None:
            obj_in.password = security.get_password_hash(obj_in.password)
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: EmailStr,
        password: str,
    ) -> User | None:
        """Authenticate a user in the database.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            email: A valid email address of the user.
            password: The password for the user.

        Returns:
            If the user is found and the password matches, the method returns
            the user object, otherwise it returns None.
        """
        db_user = (
            await self.query(db).filter_by_email(email=email).one_or_none()
        )
        if db_user and security.verify_password(password, db_user.password):
            return db_user
        return None

    async def change_role_by_id(
        self,
        db: AsyncSession,
        *,
        id: int,
        role: Role,
    ) -> User:
        """
        Change a user's role by id.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            id: The id of the user.
            role: The role to grant to the user.

        Returns:
            The user with the updated role.

        Raises:
            DoesNotExistError: Raised if the user does not exist.
        """
        db_obj = await self.get(db, id=id)
        if db_obj is None:
            raise DoesNotExistError("The user does not exist")
        db_obj.role = role
        return await self.add_record(db, db_obj=db_obj)


user = CRUDUser(User)
