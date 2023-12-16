"""The base value object for any kind of tag tag."""
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Final, Optional, Pattern, Type, TypeVar

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value

_TAG_RE: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9]*-?)*$")


_TagNameT = TypeVar("_TagNameT", bound="TagName")


@dataclass(eq=True, unsafe_hash=True)
@total_ordering
class TagName(Value):
    """The base value object for any kind of tag tag."""

    the_tag: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_tag = self._clean_the_tag(self.the_tag)

    @classmethod
    def from_raw(cls: Type[_TagNameT], tag_raw: Optional[str]) -> _TagNameT:
        """Validate and clean an tag."""
        if not tag_raw:
            raise InputValidationError("Expected tag to be non-null")

        return cls(TagName._clean_the_tag(tag_raw))

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

    @staticmethod
    def _clean_the_tag(tag_raw: str) -> str:
        tag: str = " ".join(
            word for word in tag_raw.strip().split(" ") if len(word) > 0
        )

        if len(tag) == 0:
            raise InputValidationError("Expected tag to be non-empty")

        if not _TAG_RE.match(tag):
            raise InputValidationError(
                f"Expected entity id '{tag_raw}' to match '{_TAG_RE.pattern}'",
            )

        return tag
