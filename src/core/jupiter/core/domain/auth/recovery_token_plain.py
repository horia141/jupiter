"""A recovery token for auth systems."""
import uuid

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.value import SecretValue, secret_value


@secret_value
class RecoveryTokenPlain(SecretValue):
    """A recovery token for auth systems."""

    token: str

    @staticmethod
    def new_recovery_token() -> "RecoveryTokenPlain":
        """Construct a new recovery token."""
        token = str(uuid.uuid4())
        return RecoveryTokenPlain(token)


class RecoveryTokenPlainDatabaseEncoder(
    RealmEncoder[RecoveryTokenPlain, DatabaseRealm]
):
    """Encode a password for storage in the cli."""

    def encode(self, value: RecoveryTokenPlain) -> RealmThing:
        """Encode a password hash for storage in the database."""
        return value.token


class RecoveryTokenPlainDatabaseDecoder(
    RealmDecoder[RecoveryTokenPlain, DatabaseRealm]
):
    """Decode a password hash from storage in the database."""

    def decode(self, value: RealmThing) -> RecoveryTokenPlain:
        """Decode a password hash from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password hash to be a string, got {value}"
            )

        try:
            uuid.UUID(value, version=4)
        except (ValueError, TypeError) as err:
            raise InputValidationError("Recovery token has a bad format") from err
        return RecoveryTokenPlain(value)
