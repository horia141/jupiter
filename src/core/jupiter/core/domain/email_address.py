"""An email address."""
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional, cast

from email_validator import EmailNotValidError, ValidatedEmail, validate_email
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value


@dataclass(eq=True, unsafe_hash=True)
@total_ordering
class EmailAddress(Value):
    """An email address."""

    the_address: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_address = self._clean_the_address(self.the_address)

    @staticmethod
    def from_raw(email_address_raw: Optional[str]) -> "EmailAddress":
        """Validate and clean a url."""
        if not email_address_raw:
            raise InputValidationError("Expected email address to be non-null")

        return EmailAddress(EmailAddress._clean_the_address(email_address_raw))

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EmailAddress):
            raise Exception(
                f"Cannot compare an email address with {other.__class__.__name__}",
            )
        return self.the_address < other.the_address

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_address

    @staticmethod
    def _clean_the_address(email_address_raw: str) -> str:
        email_address_str: str = email_address_raw.strip()

        try:
            email_address_fix: ValidatedEmail = validate_email(
                email_address_str,
                check_deliverability=False,
            )
            return cast(str, email_address_fix.email)
        except EmailNotValidError as err:
            raise InputValidationError(
                f"Invalid email address '{email_address_raw}'",
            ) from err