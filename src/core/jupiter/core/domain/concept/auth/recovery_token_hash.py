"""A hashed recovery token, suitable for storage."""

import argon2.profiles
from argon2 import PasswordHasher
from jupiter.core.domain.concept.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmEncoder,
    RealmThing,
    only_in_realm,
)
from jupiter.core.framework.value import SecretValue, secret_value

_PROFILE = argon2.profiles.RFC_9106_LOW_MEMORY
_PASSWORD_HASHER = PasswordHasher.from_parameters(_PROFILE)


@secret_value
@only_in_realm(DatabaseRealm)
class RecoveryTokenHash(SecretValue):
    """A hashed recovery token, suitable for storage."""

    token_hash_raw: str

    @staticmethod
    def from_plain(plain: RecoveryTokenPlain) -> "RecoveryTokenHash":
        """Build a hashed recovery token from a plain recovery token."""
        return RecoveryTokenHash(_PASSWORD_HASHER.hash(plain.token))

    def check_against(self, plain: RecoveryTokenPlain) -> bool:
        """Check that the given recovery token and this one match."""
        try:
            _PASSWORD_HASHER.verify(self.token_hash_raw, plain.token)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False


class RecoveryTokenHashDatabaseEncoder(RealmEncoder[RecoveryTokenHash, DatabaseRealm]):
    """Encode a password hash for storage in the database."""

    def encode(self, value: RecoveryTokenHash) -> RealmThing:
        """Encode a password hash for storage in the database."""
        return value.token_hash_raw


class RecoveryTokenHashDatabaseDecoder(RealmDecoder[RecoveryTokenHash, DatabaseRealm]):
    """Decode a password hash from storage in the database."""

    def decode(self, value: RealmThing) -> RecoveryTokenHash:
        """Decode a password hash from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password hash to be a string, got {value}"
            )

        try:
            recovery_token_hash_params = argon2.extract_parameters(value)
        except argon2.exceptions.InvalidHash as err:
            raise InputValidationError(
                "Hashed recovery token does not match expected format"
            ) from err

        if recovery_token_hash_params != _PROFILE:
            raise InputValidationError(
                "Hashed recovery token parameters do not match standard profile"
            )

        return RecoveryTokenHash(value)
