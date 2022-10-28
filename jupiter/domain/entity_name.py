"""The name for an entity."""
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Pattern, Final, Optional, TypeVar, Type

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_ENTITY_NAME_RE: Final[Pattern[str]] = re.compile(r"^.+$")


_EntityNameT = TypeVar("_EntityNameT", bound="EntityName")


@dataclass(frozen=True)
@total_ordering
class EntityName(Value):
    """The name for an entity which acts as both name and unique identifier."""

    _the_name: str

    @classmethod
    def from_raw(
        cls: Type[_EntityNameT], entity_name_raw: Optional[str]
    ) -> _EntityNameT:
        """Validate and clean a entity name."""
        if not entity_name_raw:
            raise InputValidationError("Expected entity name to be non-null")

        entity_name: str = " ".join(
            word for word in entity_name_raw.strip().split(" ") if len(word) > 0
        )

        if len(entity_name) == 0:
            raise InputValidationError("Expected entity name to be non-empty")

        if not _ENTITY_NAME_RE.match(entity_name):
            raise InputValidationError(
                f"Expected entity name '{entity_name_raw}' to match '{_ENTITY_NAME_RE.pattern}"
            )

        return cls(entity_name)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EntityName):
            raise Exception(
                f"Cannot compare an entity name with {other.__class__.__name__}"
            )
        return self._the_name < other._the_name

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_name
