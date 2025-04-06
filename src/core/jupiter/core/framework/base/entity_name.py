"""The name for an entity."""

import re
from functools import total_ordering
from typing import (
    Final,
    Generic,
    TypeVar,
)

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.value import AtomicValue, hashable_value

_ENTITY_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^.+$")


_EntityNameT = TypeVar("_EntityNameT", bound="EntityName")


@hashable_value
@total_ordering
class EntityName(AtomicValue[str]):
    """The name for an entity which acts as both name and unique identifier."""

    the_name: str

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


class EntityNameDatabaseEncoder(
    Generic[_EntityNameT], RealmEncoder[_EntityNameT, DatabaseRealm]
):
    """Encode an entity name for the database."""

    _the_type: type[_EntityNameT]

    def __init__(self, the_type: type[_EntityNameT]) -> None:
        """Initialize with the type of the entity name."""
        self._the_type = the_type

    def encode(self, value: _EntityNameT) -> str:
        """Encode an entity name for the database."""
        return value.the_name


class EntityNameDatabaseDecoder(
    Generic[_EntityNameT], RealmDecoder[_EntityNameT, DatabaseRealm]
):
    """Decode an entity name from the database."""

    _the_type: type[_EntityNameT]

    def __init__(self, the_type: type[_EntityNameT]) -> None:
        """Initialize with the type of the entity name."""
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _EntityNameT:
        """Decode an entity name from the database."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be a string"
            )

        entity_name: str = " ".join(
            word for word in value.strip().split(" ") if len(word) > 0
        )

        if len(entity_name) == 0:
            raise InputValidationError("Expected entity name to be non-empty")

        if not _ENTITY_NAME_RE.match(entity_name):
            raise InputValidationError(
                f"Expected entity name '{value}' to match '{_ENTITY_NAME_RE.pattern}",
            )

        return self._the_type(entity_name)


NOT_USED_NAME = EntityName("NOT-USED")
