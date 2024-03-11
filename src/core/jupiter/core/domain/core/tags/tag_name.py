"""The base value object for any kind of tag tag."""
import re
from functools import total_ordering
from typing import Final, TypeVar

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)

_TAG_RE: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9]*-?)*$")


_TagNameT = TypeVar("_TagNameT", bound="TagName")


@total_ordering
@hashable_value
class TagName(AtomicValue[str]):
    """The base value object for any kind of tag tag."""

    the_tag: str

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, TagName):
            raise Exception(
                f"Cannot compare an tag name with {other.__class__.__name__}",
            )
        return self.the_tag < other.the_tag

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_tag


class TagNameDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[TagName]):
    """Encode to a database primitive."""

    def to_primitive(self, value: TagName) -> Primitive:
        """Encode to a database primitive."""
        return value.the_tag


class TagNameDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[TagName]):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> TagName:
        """Decode from a raw string."""
        tag: str = " ".join(word for word in value.strip().split(" ") if len(word) > 0)

        if len(tag) == 0:
            raise InputValidationError("Expected tag to be non-empty")

        if not _TAG_RE.match(tag):
            raise InputValidationError(
                f"Expected entity id '{value}' to match '{_TAG_RE.pattern}'",
            )

        return TagName(tag)
