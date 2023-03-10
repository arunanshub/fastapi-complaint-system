"""
CRUD Operations.

Taken directly from tiangolo/full-stack-fastapi-postgresql.
"""
from __future__ import annotations

from .complaint import complaint
from .transaction import transaction
from .user import user

__all__ = ["user", "complaint", "transaction"]
