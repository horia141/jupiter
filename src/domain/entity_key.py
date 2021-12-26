"""The key for an entity which acts as both name and unique identifier."""
import abc
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Pattern, Final, Optional, TypeVar, Type

from framework.errors import InputValidationError
from framework.value import Value

_ENTITY_KEY_RE: Final[Pattern[str]] = re.compile(r"^[a-z0-9]([a-z0-9]*-?)*$")


_EntityKeyType = TypeVar('_EntityKeyType', bound='EntityKey')


@dataclass(frozen=True)
@total_ordering
class EntityKey(Value, abc.ABC):
    """The key for a entity which acts as both name and unique identifier."""

    _the_key: str

    @classmethod
    def from_raw(cls: Type[_EntityKeyType], entity_key_raw: Optional[str]) -> _EntityKeyType:
        """Validate and clean a entity key."""
        if not entity_key_raw:
            raise InputValidationError("Expected entity key key to be non-null")

        entity_key_str: str = entity_key_raw.strip().lower()

        if len(entity_key_str) == 0:
            raise InputValidationError("Expected entity key to be non-empty")

        if not _ENTITY_KEY_RE.match(entity_key_str):
            raise InputValidationError(
                f"Expected entity key '{entity_key_raw}' to match '{_ENTITY_KEY_RE.pattern}'")

        return cls(entity_key_str)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, EntityKey):
            raise Exception(f"Cannot compare an entity id with {other.__class__.__name__}")
        return self._the_key < other._the_key

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_key
