"""Common errors."""


class RepositoryError(Exception):
    """An exception raised when loading data from a repository."""


class ModelValidationError(Exception):
    """An exception raised when validating some model type."""
