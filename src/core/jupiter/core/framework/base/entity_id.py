"""A generic entity id."""
import re
import typing
from dataclasses import dataclass
from functools import total_ordering

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value

_ENTITY_ID_RE: typing.Pattern[str] = re.compile(r"^\d+|[a-zA-Z0-9_]+|bad-entity-id$")


@dataclass(eq=True, unsafe_hash=True)
@total_ordering
class EntityId(Value):
    """A generic entity id."""

    the_id: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_id = self._clean_the_id(self.the_id)

    @staticmethod
    def from_raw(entity_id_raw: object) -> "EntityId":
        """Validate and clean an entity id."""
        if not isinstance(entity_id_raw, str):
            raise InputValidationError("Expected entity id to be string")
        if not entity_id_raw:
            raise InputValidationError("Expected entity id to be non-null")

        return EntityId(EntityId._clean_the_id(entity_id_raw))

    def as_int(self) -> int:
        """Return an integer form of this, if possible."""
        if self.the_id == "bad-entity-id":
            return -1
        return int(self.the_id)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EntityId):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )
        return self.the_id < other.the_id

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_id

    @staticmethod
    def _clean_the_id(entity_id_raw: str) -> str:
        entity_id: str = entity_id_raw.strip()

        if len(entity_id) == 0:
            raise InputValidationError("Expected entity id to be non-empty")

        if not _ENTITY_ID_RE.match(entity_id):
            raise InputValidationError(
                f"Expected entity id '{entity_id_raw}' to match '{_ENTITY_ID_RE.pattern}",
            )

        return entity_id


BAD_REF_ID = EntityId("bad-entity-id")
