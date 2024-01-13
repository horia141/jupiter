"""The name for an entity."""
import re
from functools import total_ordering
from typing import (
    Final,
    Pattern,
    Type,
    TypeVar,
)

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value

_ENTITY_NAME_RE: Final[Pattern[str]] = re.compile(r"^.+$")


_EntityNameT = TypeVar("_EntityNameT", bound="EntityName")


@hashable_value
@total_ordering
class EntityName(AtomicValue):
    """The name for an entity which acts as both name and unique identifier."""

    the_name: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_name = self._clean_the_name(self.the_name)

    @classmethod
    def from_raw(
        cls: Type[_EntityNameT],
        value: Primitive,
    ) -> _EntityNameT:
        """Validate and clean an entity name."""
        if not isinstance(value, str):
            raise InputValidationError("Expected entity name to be non-null")

        entity_name = EntityName._clean_the_name(value)

        return cls(entity_name)

    def to_primitive(self) -> Primitive:
        return self.the_name

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EntityName):
            raise Exception(
                f"Cannot compare an entity name with {other.__class__.__name__}",
            )
        return self.the_name < other.the_name

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_name

    @staticmethod
    def _clean_the_name(entity_name_raw: str) -> str:
        entity_name: str = " ".join(
            word for word in entity_name_raw.strip().split(" ") if len(word) > 0
        )

        if len(entity_name) == 0:
            raise InputValidationError("Expected entity name to be non-empty")

        if not _ENTITY_NAME_RE.match(entity_name):
            raise InputValidationError(
                f"Expected entity name '{entity_name_raw}' to match '{_ENTITY_NAME_RE.pattern}",
            )

        return entity_name


NOT_USED_NAME = EntityName("NOT-USED")
