"""The base value object for any kind of tag tag."""
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Final, Pattern, Optional, TypeVar, Type

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_TAG_RE: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9]*-?)*$")


_TagNameType = TypeVar('_TagNameType', bound='TagName')


@dataclass(frozen=True)
@total_ordering
class TagName(Value):
    """The base value object for any kind of tag tag."""

    _the_tag: str

    @classmethod
    def from_raw(cls: Type[_TagNameType], tag_raw: Optional[str]) -> _TagNameType:
        """Validate and clean an tag."""
        if not tag_raw:
            raise InputValidationError("Expected tag to be non-null")

        tag: str = " ".join(word for word in tag_raw.strip().split(" ") if len(word) > 0)

        if len(tag) == 0:
            raise InputValidationError("Expected tag to be non-empty")

        if not _TAG_RE.match(tag):
            raise InputValidationError(
                f"Expected entity id '{tag_raw}' to match '{_TAG_RE.pattern}'")

        return cls(tag)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, TagName):
            raise Exception(f"Cannot compare an tag name with {other.__class__.__name__}")
        return self._the_tag < other._the_tag

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_tag
