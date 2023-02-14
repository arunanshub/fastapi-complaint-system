from __future__ import annotations

import typing

import asyncclick as click

if typing.TYPE_CHECKING:
    from pydantic import EmailStr


@click.group()
async def cli() -> None:
    """Helper commands for managing the application."""


@cli.command()
@click.option("-f", "--first-name", type=str, required=True)
@click.option("-l", "--last-name", type=str, required=True)
@click.option("-e", "--email", type=str, required=True)
@click.option("-n", "--phone", type=str, required=True)
@click.option("-i", "--iban", type=str, required=True)
@click.option(
    "-p",
    "--password",
    type=str,
    required=True,
    prompt=True,
    hide_input=True,
)
async def create_admin(
    first_name: str,
    last_name: str,
    email: EmailStr,
    phone: str,
    iban: str,
    password: str,
) -> None:
    """
    Create an admin user.
    """
    # localize imports for faster script startup
    from .crud import user
    from .database import get_db
    from .models.enums import Role
    from .models.user import UserCreate

    user_in = UserCreate(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        iban=iban,
        password=password,
    )
    async for db in get_db():
        # PERF: we can improve this by directly creating the user with
        # the role.
        db_user = await user.create(db, obj_in=user_in)
        assert db_user.id is not None
        await user.change_role_by_id(db, id=db_user.id, role=Role.ADMIN)


if __name__ == "__main__":
    cli()
