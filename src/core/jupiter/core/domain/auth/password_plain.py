"""A password in plain text, as received from a user."""
from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import DatabaseRealm, RealmDecoder, RealmEncoder, RealmThing
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


class PasswordPlainDatabaseEncoder(RealmEncoder[PasswordPlain, DatabaseRealm]):
    """Encode a password plain for storage in the database."""

    def encode(self, value: PasswordPlain) -> RealmThing:
        """Encode a password plain for storage in the database."""
        return value.password_raw


class PasswordPlainDatabaseDecoder(RealmDecoder[PasswordPlain, DatabaseRealm]):
    """Decode a password plain from storage in the database."""

    def decode(self, value: RealmThing) -> PasswordPlain:
        """Decode a password plain from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password plain to be a string, got {value}"
            )
        return PasswordPlain.from_raw(value)
