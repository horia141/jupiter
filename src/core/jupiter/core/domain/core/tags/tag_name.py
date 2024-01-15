"""The base value object for any kind of tag tag."""
import re
from functools import total_ordering
from typing import Final, Pattern, Type, TypeVar

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value

_TAG_RE: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9]*-?)*$")


_TagNameT = TypeVar("_TagNameT", bound="TagName")


@total_ordering
@hashable_value
class TagName(AtomicValue):
    """The base value object for any kind of tag tag."""

    the_tag: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_tag = self._clean_the_tag(self.the_tag)

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls: Type[_TagNameT], tag_raw: Primitive) -> _TagNameT:
        """Validate and clean an tag."""
        if not isinstance(tag_raw, str):
            raise InputValidationError("Expected tag to be a string")

        return cls(TagName._clean_the_tag(tag_raw))

    def to_primitive(self) -> Primitive:
        return self.the_tag

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
