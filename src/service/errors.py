"""Errors raised by services."""


class ServiceError(Exception):
    """Exception raised by the vacation service."""


class ServiceValidationError(ServiceError):
    """Exception raised by the vacation service when inputs don't validate."""
