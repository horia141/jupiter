"""A recovery token for auth systems."""

import uuid
from dataclasses import dataclass
from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.secret_value import SecretValue
from jupiter.core.framework.secure import secure_class


@dataclass(repr=False)
@secure_class
class RecoveryTokenPlain(SecretValue):
    """A recovery token for auth systems."""

    token: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        token = self._clean_token(self.token)
        self.token = token

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
