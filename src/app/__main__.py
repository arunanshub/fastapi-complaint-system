from __future__ import annotations

import sys
import typing

import asyncclick as click
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

from . import main

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


@cli.command()
@click.option("-m", "--max-tries", type=int, default=60 * 5, show_default=True)
@click.option("-w", "--wait-seconds", type=int, default=5, show_default=True)
async def pre_start(max_tries: int, wait_seconds: int) -> None:
    """Check if all services are functional.

    If not functional, retry.
    """

    @retry(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
    )
    async def retrier() -> None:
        await main.check_services()

    try:
        await retrier()
    except RetryError:
        click.secho("Error in system!", fg="red")
        sys.exit(1)

    click.secho("Everything is functional", fg="green")


if __name__ == "__main__":
    cli()
