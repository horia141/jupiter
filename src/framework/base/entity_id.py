"""A generic entity id."""
import re
import typing
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from framework.errors import InputValidationError
from framework.value import Value

_ENTITY_ID_RE: typing.Pattern[str] = re.compile(r"^\d+$")


@dataclass(frozen=True)
@total_ordering
class EntityId(Value):
    """A generic entity id."""

    _the_id: str

    @staticmethod
    def from_raw(entity_id_raw: Optional[str]) -> 'EntityId':
        """Validate and clean an entity id."""
        if not entity_id_raw:
            raise InputValidationError("Expected entity id to be non-null")

        entity_id: str = entity_id_raw.strip()

        if len(entity_id) == 0:
            raise InputValidationError("Expected entity id to be non-empty")

        if not _ENTITY_ID_RE.match(entity_id):
            raise InputValidationError(
                f"Expected entity id '{entity_id_raw}' to match '{_ENTITY_ID_RE.pattern}")

        return EntityId(entity_id)

    def as_int(self) -> int:
        """Return an integer form of this, if possible."""
        return int(self._the_id)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EntityId):
            raise Exception(f"Cannot compare an entity id with {other.__class__.__name__}")
        return self._the_id < other._the_id

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_id


BAD_REF_ID = EntityId("bad-entity-id")
