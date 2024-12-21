"""An externally facing authentication token."""
import re
from re import Pattern
from typing import Final

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)

_JWT_RE: Final[Pattern[str]] = re.compile(
    r"([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)"
)


@value
@secure_class
class AuthTokenExt(AtomicValue[str]):
    """An externally facing authentication token."""

    auth_token_str: str


class AutoTokenExtDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[AuthTokenExt]):
    """Encode to a database primitive."""

    def to_primitive(self, value: AuthTokenExt) -> str:
        """Encode to a database primitive."""
        return value.auth_token_str


class AuthTokenExtDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[AuthTokenExt]):
    """Decode from a database primitive."""

    def from_raw_str(self, primitive: str) -> AuthTokenExt:
        """Decode from a raw string."""
        if not _JWT_RE.match(primitive):
            raise InputValidationError("Expected auth token to be a valid JWT")
        return AuthTokenExt(primitive)
