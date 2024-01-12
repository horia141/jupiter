"""An externally facing authentication token."""
import re
from re import Pattern
from typing import Final

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.value import AtomicValue, Value, value

_JWT_RE: Final[Pattern[str]] = re.compile(
    r"([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)"
)


@value
@secure_class
class AuthTokenExt(AtomicValue):
    """An externally facing authentication token."""

    auth_token_str: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        auth_token_str = AuthTokenExt._clean_auth_token(self.auth_token_str)
        self.auth_token_str = auth_token_str

    @staticmethod
    def from_raw(auth_token_raw: str) -> "AuthTokenExt":
        """Build an auth token from the raw representation."""
        auth_token_str = AuthTokenExt._clean_auth_token(auth_token_raw)
        return AuthTokenExt(auth_token_str)

    @staticmethod
    def _clean_auth_token(auth_token_str_raw: str) -> str:
        if not _JWT_RE.match(auth_token_str_raw):
            raise InputValidationError("Expected auth token to be a valid JWT")
        return auth_token_str_raw
