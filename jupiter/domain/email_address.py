"""An email address."""
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from email_validator import EmailNotValidError, validate_email

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
@total_ordering
class EmailAddress(Value):
    """An email address."""

    _the_address: str

    @staticmethod
    def from_raw(email_address_raw: Optional[str]) -> "EmailAddress":
        """Validate and clean a url."""
        if not email_address_raw:
            raise InputValidationError("Expected email address to be non-null")

        email_address_str: str = email_address_raw.strip()

        try:
            email_address_fix = validate_email(
                email_address_str, check_deliverability=False
            )
            return EmailAddress(email_address_fix.email)
        except EmailNotValidError as err:
            raise InputValidationError(
                f"Invalid email address '{email_address_raw}'"
            ) from err

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EmailAddress):
            raise Exception(
                f"Cannot compare an email address with {other.__class__.__name__}"
            )
        return self._the_address < other._the_address

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_address
