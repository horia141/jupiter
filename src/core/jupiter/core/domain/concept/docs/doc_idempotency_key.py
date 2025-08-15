"""A document idempotency key in this domain."""

from functools import total_ordering

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@value
@total_ordering
class DocIdempotencyKey(AtomicValue[str]):
    """A document idempotency key in this domain."""

    the_key: str

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, DocIdempotencyKey):
            raise Exception(
                f"Cannot compare a document idempotency key with {other.__class__.__name__}",
            )
        return self.the_key < other.the_key

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_key


class DocIdempotencyKeyDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[DocIdempotencyKey]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: DocIdempotencyKey) -> Primitive:
        """Encode to a database primitive."""
        return value.the_key


class DocIdempotencyKeyDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[DocIdempotencyKey]
):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> DocIdempotencyKey:
        """Decode from a raw string."""
        if not value or not value.strip():
            raise InputValidationError("Document idempotency key cannot be empty")

        if len(value) <= 3:
            raise InputValidationError(
                "Document idempotency key must be longer than 3 characters"
            )

        if len(value) > 36:
            raise InputValidationError(
                "Document idempotency key must be shorter than 36 characters"
            )

        return DocIdempotencyKey(value)
