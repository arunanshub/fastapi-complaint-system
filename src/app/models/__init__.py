from __future__ import annotations

from sqlmodel import SQLModel

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# NOTE: The naming convention must be assigned before the models are loaded.
metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION


from . import complaint, user  # noqa: E402

__all__ = ["metadata", "user", "complaint"]
