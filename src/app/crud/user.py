"""Module for User CRUD operations."""
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from pydantic import EmailStr
    from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel import select

from ..core import security
from ..models.user import User, UserCreate, UserUpdate
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    This class is a subclass of ``CRUDBase`` that is specific to the ``User``
    model. It extends the base class to provide additional methods specific to
    the User model.
    """

    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: EmailStr,
    ) -> User | None:
        """Retrieve a single User record by email.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            email: A vaild email address as string.

        Returns:
            ``User`` if user is found, ``None`` otherwise.
        """
        stmt = select(User).where(User.email == email)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Creates a new user in the database.

        Before ading the user in the database, the user's password is hashed.

        Args:
            db:
                Asynchronous SQLAlchemy session object used to perform database
                operations.

        Keyword Args:
            obj_in:
                Data for the new user that will be inserted into the database.

        Returns:
            The created database object.
        """
        obj_in.password = security.get_password_hash(obj_in.password)
        return await super().create(db, obj_in=obj_in)

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
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_password(password, user.password):
            return None
        return user


user = CRUDUser(User)
