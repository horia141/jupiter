"""The name for an entity."""
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import (
    Final,
    Optional,
    Pattern,
    Type,
    TypeVar,
)

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value

_ENTITY_NAME_RE: Final[Pattern[str]] = re.compile(r"^.+$")


_EntityNameT = TypeVar("_EntityNameT", bound="EntityName")


@dataclass(eq=True, unsafe_hash=True)
@total_ordering
class EntityName(Value):
    """The name for an entity which acts as both name and unique identifier."""

    the_name: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_name = self._clean_the_name(self.the_name)

    @classmethod
    def from_raw(
        cls: Type[_EntityNameT],
        entity_name_raw: Optional[str],
    ) -> _EntityNameT:
        """Validate and clean an entity name."""
        if not entity_name_raw:
            raise InputValidationError("Expected entity name to be non-null")

        entity_name = EntityName._clean_the_name(entity_name_raw)

        return cls(entity_name)

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
