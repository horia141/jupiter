"""The relationship the user has with a person."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from models.framework import Value
from models.errors import ModelValidationError


@enum.unique
class PersonRelationship(Value, enum.Enum):
    """The relationship the user has with a person."""
    FAMILY = "family"
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"
    SCHOOL_BUDDY = "school-buddy"
    WORK_BUDDY = "work-buddy"
    COLLEAGUE = "colleague"
    OTHER = "other"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @staticmethod
    def from_raw(person_relationship_raw: Optional[str]) -> 'PersonRelationship':
        """Validate and clean a raw person relationship value."""
        if not person_relationship_raw:
            raise ModelValidationError("Expected sync target to be non-null")

        person_relationship_str: str = person_relationship_raw.strip().lower()

        if person_relationship_str not in PersonRelationship.all_values():
            raise ModelValidationError(
                f"Expected sync prefer '{person_relationship_raw}' to be one of " +
                f"'{','.join(PersonRelationship.all_values())}'")

        return PersonRelationship(person_relationship_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for sync targets."""
        return frozenset(st.value for st in PersonRelationship)
