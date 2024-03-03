"""An email address."""
from functools import total_ordering
from typing import cast

from email_validator import EmailNotValidError, ValidatedEmail, validate_email
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@hashable_value
@total_ordering
class EmailAddress(AtomicValue[str]):
    """An email address."""

    the_address: str

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


class EmailAddressDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[EmailAddress]):
    """Encode to a database primitive."""

    def to_primitive(self, value: EmailAddress) -> str:
        """Encode to a database primitive."""
        return value.the_address


class EmailAddressDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[EmailAddress]):
    """Decode from a database primitive."""

    def from_raw_str(self, primitive: str) -> EmailAddress:
        """Decode from a raw string."""
        email_address_str: str = primitive.strip()

        try:
            email_address_fix: ValidatedEmail = validate_email(
                email_address_str,
                check_deliverability=False,
            )
            return EmailAddress(cast(str, email_address_fix.email))
        except EmailNotValidError as err:
            raise InputValidationError(
                f"Invalid email address '{primitive}'",
            ) from err
