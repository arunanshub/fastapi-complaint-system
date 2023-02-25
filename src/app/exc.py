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


class UploadFailedError(Exception):
    """
    Exception class representing an error that occurs when upload fails.
    """


class FailedTransactionError(Exception):
    """
    Exception class representing an error that occurs when a bank transaction
    fails.
    """
