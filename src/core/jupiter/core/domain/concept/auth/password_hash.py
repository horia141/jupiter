"""A hashed password, suitable for storage."""

import argon2.profiles
from argon2 import PasswordHasher
from jupiter.core.domain.concept.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.concept.auth.password_plain import PasswordPlain
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
class PasswordHash(SecretValue):
    """A hashed password, suitable for storage."""

    password_hash_raw: str

    @staticmethod
    def from_raw(password_hash_str: str | None) -> "PasswordHash":
        """Validate and clean a raw hashed password."""
        if not password_hash_str:
            raise InputValidationError("Expected hashed password to be non-null")

        try:
            password_hash_params = argon2.extract_parameters(password_hash_str)
        except argon2.exceptions.InvalidHash as err:
            raise InputValidationError(
                "Hashed password does not match expected format"
            ) from err

        if password_hash_params != _PROFILE:
            raise InputValidationError(
                "Hashed password parameters do not match standard profile"
            )

        return PasswordHash(password_hash_str)

    @staticmethod
    def from_new_plain(plain: PasswordNewPlain) -> "PasswordHash":
        """Build a hashed password from a new plain password."""
        return PasswordHash(_PASSWORD_HASHER.hash(plain.password_raw))

    def check_against(self, plain: PasswordPlain) -> bool:
        """Check that the given password and this one match."""
        try:
            _PASSWORD_HASHER.verify(self.password_hash_raw, plain.password_raw)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False


class PasswordHashDatabaseEncoder(RealmEncoder[PasswordHash, DatabaseRealm]):
    """Encode a password hash for storage in the database."""

    def encode(self, value: PasswordHash) -> RealmThing:
        """Encode a password hash for storage in the database."""
        return value.password_hash_raw


class PasswordHashDatabaseDecoder(RealmDecoder[PasswordHash, DatabaseRealm]):
    """Decode a password hash from storage in the database."""

    def decode(self, value: RealmThing) -> PasswordHash:
        """Decode a password hash from storage in the database."""
        if not isinstance(value, str):
            raise InputValidationError(
                f"Expected password hash to be a string, got {value}"
            )
        return PasswordHash.from_raw(value)
