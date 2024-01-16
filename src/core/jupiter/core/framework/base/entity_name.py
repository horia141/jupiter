"""The name for an entity."""
import re
from functools import total_ordering
from typing import (
    Final,
    Generic,
    Pattern,
    Type,
    TypeVar,
)

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
)
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
    def base_type_hack(cls) -> type[Primitive]:
        return str

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

        return self._the_type.from_raw(value)


NOT_USED_NAME = EntityName("NOT-USED")
