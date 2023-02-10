# isort: dont-add-imports
from pydantic import EmailStr  # noqa: TC002
from sqlmodel import Field, SQLModel

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


class User(UserBase, table=True):  # type: ignore[call-arg]
    id: int | None = Field(default=None, primary_key=True)
    password: str = Field(max_length=255)
