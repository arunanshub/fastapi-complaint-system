# isort: dont-add-imports
from pydantic import EmailStr  # noqa: TC002
from sqlmodel import Field, Relationship, SQLModel

from .base import SQLBase
from .enums import Role


class UserBase(SQLModel):
    email: EmailStr | None = Field(unique=True)
    first_name: str | None = Field(max_length=200)
    last_name: str | None = Field(max_length=200)
    phone: str | None = Field(max_length=20)
    role: Role | None = Field(
        default=None,
        nullable=False,
        sa_column_kwargs={
            "server_default": Role.COMPLAINER.name,
        },
    )
    iban: str | None = Field(max_length=200)


class UserCreate(SQLModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    iban: str
    password: str


class UserRead(SQLModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: Role
    phone: str
    iban: str


class UserReadWithComplaints(UserRead):
    complaints: list["ComplaintRead"]


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(unique=True)
    first_name: str | None = Field(max_length=200)
    last_name: str | None = Field(max_length=200)
    phone: str | None = Field(max_length=20)
    iban: str | None = Field(max_length=200)
    password: str | None = Field(max_length=255)


class User(SQLBase, UserBase, table=True):  # type: ignore[call-arg]
    password: str = Field(max_length=255)
    complaints: list["Complaint"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "raise"},
    )


from .complaint import Complaint, ComplaintRead  # noqa: E402,TC002

UserReadWithComplaints.update_forward_refs(ComplaintRead=ComplaintRead)
