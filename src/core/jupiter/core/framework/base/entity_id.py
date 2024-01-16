"""A generic entity id."""
import re
import typing
from functools import total_ordering

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmConcept,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
)
from jupiter.core.framework.value import AtomicValue, hashable_value

_ENTITY_ID_RE: typing.Pattern[str] = re.compile(r"^\d+|[a-zA-Z0-9_]+|bad-entity-id$")


@hashable_value
@total_ordering
class EntityId(AtomicValue):
    """A generic entity id."""

    the_id: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_id = self._clean_the_id(self.the_id)

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "EntityId":
        """Validate and clean an entity id."""
        if not isinstance(value, (str, int)):
            raise InputValidationError("Expected entity id to be string")
        
        if isinstance(value, int):
            if value == -1:
                return BAD_REF_ID
            if value < 0:
                raise InputValidationError(
                    "Expected entity id to be a positive integer"
                )
            return EntityId(str(value))

        return EntityId(EntityId._clean_the_id(value))

    def as_int(self) -> int:
        """Return an integer form of this, if possible."""
        if self.the_id == "bad-entity-id":
            return -1
        return int(self.the_id)

    def to_primitive(self) -> Primitive:
        return self.the_id

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
            raise RealmDecodingError("Expected entity id to be non-empty")

        if not _ENTITY_ID_RE.match(entity_id):
            raise RealmDecodingError(
                f"Expected entity id '{entity_id_raw}' to match '{_ENTITY_ID_RE.pattern}",
            )

        return entity_id


class EntityIdDatabaseEncoder(RealmEncoder[EntityId, DatabaseRealm]):
    """Entity id encoder for the database realm."""

    def encode(self, value: EntityId) -> RealmConcept:
        return value.as_int()


class EntityIdDatabaseDecoder(RealmDecoder[EntityId, DatabaseRealm]):
    """Entity id decoder for the database realm."""

    def decode(self, value: RealmConcept) -> EntityId:
        if not isinstance(value, (int, str)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be an int or string"
            )

        return EntityId.from_raw(value)


BAD_REF_ID = EntityId("bad-entity-id")
