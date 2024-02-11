"""An externally facing authentication token."""
import re
from re import Pattern
from typing import Final

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseDecoder, PrimitiveAtomicValueDatabaseEncoder

_JWT_RE: Final[Pattern[str]] = re.compile(
    r"([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)"
)


@value
@secure_class
class AuthTokenExt(AtomicValue):
    """An externally facing authentication token."""

    auth_token_str: str

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        """Get the base type of this value."""
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "AuthTokenExt":
        """Build an auth token from the raw representation."""
        if not isinstance(value, str):
            raise InputValidationError("Expected auth token to be a string")
        auth_token_str = AuthTokenExt._clean_auth_token(value)
        return AuthTokenExt(auth_token_str)

    def to_primitive(self) -> Primitive:
        return self.auth_token_str

    @staticmethod
    def _clean_auth_token(auth_token_str_raw: str) -> str:
        if not _JWT_RE.match(auth_token_str_raw):
            raise InputValidationError("Expected auth token to be a valid JWT")
        return auth_token_str_raw

class AutoTokenExtDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[AuthTokenExt, str]):

    def to_primitive(self, value: AuthTokenExt) -> str:
        return value.auth_token_str
    

class AuthTokenExtDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[AuthTokenExt, str]):

    def from_raw(self, primitive: str) -> AuthTokenExt:
        if not _JWT_RE.match(primitive):
            raise InputValidationError("Expected auth token to be a valid JWT")
        return AuthTokenExt(primitive)