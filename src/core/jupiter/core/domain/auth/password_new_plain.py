"""A new password in plain text, as received from a user."""
import re
from re import Pattern
from typing import Final, Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.value import SecretValue, secret_value

_PASSWORD_PLAIN_RE: Final[Pattern[str]] = re.compile(r"^\S+$")
_PASSWORD_MIN_LENGTH: Final[int] = 10


@secret_value
class PasswordNewPlain(SecretValue):
    """A new password in plain text, as received from a user."""

    password_raw: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        password_raw = self._clean_password(self.password_raw)
        self.password_raw = password_raw

    @staticmethod
    def from_raw(password_str: Optional[str]) -> "PasswordNewPlain":
        """Validate and clean a raw password."""
        if not password_str:
            raise InputValidationError("Expected password to be non null")

        password_str = PasswordNewPlain._clean_password(password_str)

        return PasswordNewPlain(password_str)

    @staticmethod
    def _clean_password(password_str_raw: str) -> str:
        if not _PASSWORD_PLAIN_RE.match(password_str_raw):
            raise InputValidationError(
                "Expected password to not contain any white-space"
            )

        if len(password_str_raw) < _PASSWORD_MIN_LENGTH:
            raise InputValidationError(
                f"Expected password to be longer than {_PASSWORD_MIN_LENGTH} characters"
            )

        return password_str_raw


class PasswordNewPlainDatabaseEncoder(RealmEncoder[PasswordNewPlain, DatabaseRealm]):
    """Encode a password newplain for storage in the database."""

    def encode(self, value: PasswordNewPlain) -> RealmThing:
        """Encode a password newplain for storage in the database."""
        return value.password_raw


class PasswordNewPlainDatabaseDecoder(RealmDecoder[PasswordNewPlain, DatabaseRealm]):
    """Decode a password newplain from storage in the database."""

    def decode(self, value: RealmThing) -> PasswordNewPlain:
        """Decode a password newplain from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password newplain to be a string, got {value}"
            )
        return PasswordNewPlain.from_raw(value)
