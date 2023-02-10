from __future__ import annotations

import enum


class Role(enum.Enum):
    APPROVER = "approver"
    COMPLAINER = "complainer"
    ADMIN = "admin"


class ComplaintStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
