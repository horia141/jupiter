"""A password in plain text, as received from a user."""
import re
from re import Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    CliRealm,
    EventStoreRealm,
    RealmDecoder,
    RealmEncoder,
    RealmThing,
    WebRealm,
    only_in_realm,
)
from jupiter.core.framework.value import SecretValue, secret_value

_PASSWORD_PLAIN_RE: Pattern[str] = re.compile(r"^\S+$")
_PASSWORD_MIN_LENGTH: int = 10


@secret_value
@only_in_realm(CliRealm, WebRealm, EventStoreRealm)
class PasswordPlain(SecretValue):
    """A new password in plain text, as received from a user."""

    password_raw: str


class PasswordPlainCliDecoder(RealmDecoder[PasswordPlain, CliRealm]):
    """Decode a password newplain from storage in the CLI."""

    def decode(self, value: RealmThing) -> PasswordPlain:
        """Decode a password plain from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password newplain to be a string, got {value}"
            )

        if not _PASSWORD_PLAIN_RE.match(value):
            raise InputValidationError(
                "Expected password to not contain any white-space"
            )

        if len(value) < _PASSWORD_MIN_LENGTH:
            raise InputValidationError(
                f"Expected password to be longer than {_PASSWORD_MIN_LENGTH} characters"
            )

        return PasswordPlain(value)


class PasswordPlainWebDecoder(RealmDecoder[PasswordPlain, WebRealm]):
    """Decode a password newplain from storage in the Web."""

    def decode(self, value: RealmThing) -> PasswordPlain:
        """Decode a password newplain from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password newplain to be a string, got {value}"
            )

        if not _PASSWORD_PLAIN_RE.match(value):
            raise InputValidationError(
                "Expected password to not contain any white-space"
            )

        if len(value) < _PASSWORD_MIN_LENGTH:
            raise InputValidationError(
                f"Expected password to be longer than {_PASSWORD_MIN_LENGTH} characters"
            )

        return PasswordPlain(value)


class PasswordPlainEventStoreRealmEncoder(RealmEncoder[PasswordPlain, EventStoreRealm]):
    """Encode a password newplain for storage in the Event Store."""

    def encode(self, value: PasswordPlain) -> RealmThing:
        """Encode a password newplain for storage in the Event Store."""
        return "***********"