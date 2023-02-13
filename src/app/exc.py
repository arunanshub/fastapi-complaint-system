from __future__ import annotations


class NotUniqueError(Exception):
    """
    Exception class representing an error that occurs when a unique constraint
    is violated.
    """


class DoesNotExistError(Exception):
    """
    Exception class representing an error that occurs when a database record is
    not found.
    """
