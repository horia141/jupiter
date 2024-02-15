"""An URL in this domain."""
from functools import total_ordering

import validators
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@value
@total_ordering
class URL(AtomicValue[str]):
    """A URL in this domain."""

    the_url: str

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, URL):
            raise Exception(f"Cannot compare an URL {other.__class__.__name__}")
        return self.the_url < other.the_url

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_url


class URLDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[URL]):
    def to_primitive(self, value: URL) -> Primitive:
        return value.the_url


class URLDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[URL]):
    def from_raw_str(self, value: str) -> URL:
        url_str: str = value.strip()

        validation_result = validators.url(url_str)
        if validation_result is not True:
            raise InputValidationError(f"Invalid URL '{value}'")
        return URL(url_str)
