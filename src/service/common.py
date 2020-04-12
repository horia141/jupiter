"""Common defines for all repositories."""
from typing import NewType


RefId = NewType("RefId", str)


class RepositoryError(Exception):
    """An exception raised when loading data from a repository."""
