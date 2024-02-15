"""A recovery token for auth systems."""

import uuid
from typing import Optional

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

    @staticmethod
    def from_raw(recovery_token_raw: Optional[str]) -> "RecoveryTokenPlain":
        """Validate and clean a raw recovery token."""
        if recovery_token_raw is None:
            raise InputValidationError("Expected recovery token to non-null")

        token = RecoveryTokenPlain._clean_token(recovery_token_raw)

        return RecoveryTokenPlain(token)

    @staticmethod
    def _clean_token(token_str: str) -> str:
        try:
            uuid.UUID(token_str, version=4)
        except (ValueError, TypeError) as err:
            raise InputValidationError("Recovery token has a bad format") from err
        return token_str


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
        return RecoveryTokenPlain.from_raw(value)
