"""A password in plain text, as received from a user."""
from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import SecretValue, secret_value


@secret_value
class PasswordPlain(SecretValue):
    """A new password in plain text, as received from a user."""

    password_raw: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        password_raw = self._clean_password(self.password_raw)
        self.password_raw = password_raw

    @staticmethod
    def from_raw(password_str: Optional[str]) -> "PasswordPlain":
        """Validate and clean a raw password."""
        if not password_str:
            raise InputValidationError("Expected password to be non null")

        password_str = PasswordPlain._clean_password(password_str)

        return PasswordPlain(password_str)

    @staticmethod
    def _clean_password(password_str_raw: str) -> str:
        if len(password_str_raw) == 0:
            raise InputValidationError("Expected password to be non-empty")

        return password_str_raw
