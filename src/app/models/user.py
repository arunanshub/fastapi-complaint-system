# isort: dont-add-imports
from pydantic import EmailStr  # noqa: TC002
from sqlmodel import Field, SQLModel

from .base import SQLBase
from .enums import Role


class UserBase(SQLModel):
    email: EmailStr | None = Field(unique=True)
    first_name: str | None = Field(max_length=200)
    last_name: str | None = Field(max_length=200)
    phone: str | None = Field(max_length=20)
    role: Role = Field(
        sa_column_kwargs={
            "server_default": Role.COMPLAINER.name,
        }
    )
    iban: str | None = Field(max_length=200)


class UserCreate(SQLModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: Role
    password: str


class UserRead(SQLModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: Role
    phone: str | None
    iban: str | None


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(unique=True)
    first_name: str | None = Field(max_length=200)
    last_name: str | None = Field(max_length=200)
    phone: str | None = Field(max_length=20)
    role: Role | None
    iban: str | None = Field(max_length=200)
    password: str | None = Field(max_length=255)


class User(SQLBase, UserBase, table=True):  # type: ignore[call-arg]
    password: str = Field(max_length=255)
