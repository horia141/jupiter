"""Common errors."""

from collections.abc import Mapping


class InputValidationError(ValueError):
    """An exception raised when validating some model type."""


class MultiInputValidationError(ValueError):
    """An exception raised when validating multiple model types."""

    _errors: dict[str, InputValidationError]

    def __init__(self, errors: dict[str, InputValidationError]):
        """Constructor."""
        self._errors = errors

    @property
    def errors(self) -> Mapping[str, InputValidationError]:
        """The errors."""
        return self._errors
