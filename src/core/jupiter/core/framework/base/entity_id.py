"""A generic entity id."""
import re
import typing
from functools import total_ordering

from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
    WebRealm,
)
from jupiter.core.framework.value import AtomicValue, hashable_value

_ENTITY_ID_RE: typing.Pattern[str] = re.compile(r"^\d+|[a-zA-Z0-9_]+|bad-entity-id$")


@hashable_value
@total_ordering
class EntityId(AtomicValue[str]):
    """A generic entity id."""

    the_id: str

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


class EntityIdDatabaseEncoder(RealmEncoder[EntityId, DatabaseRealm]):
    """Entity id encoder for the database realm."""

    def encode(self, value: EntityId) -> RealmThing:
        return value.as_int()


class EntityIdWebEncoder(RealmEncoder[EntityId, WebRealm]):
    """Entity id encoder for the database realm."""

    def encode(self, value: EntityId) -> RealmThing:
        return value.the_id


class EntityIdDatabaseDecoder(RealmDecoder[EntityId, DatabaseRealm]):
    """Entity id decoder for the database realm."""

    def decode(self, value: RealmThing) -> EntityId:
        if not isinstance(value, (int, str)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be an int or string"
            )

        return EntityId(str(value))


BAD_REF_ID = EntityId("bad-entity-id")
