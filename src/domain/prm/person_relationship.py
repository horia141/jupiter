"""The relationship the user has with a person."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from models.framework import Value, ModelValidationError


@enum.unique
class PersonRelationship(enum.Enum, Value):
    """The relationship the user has with a person."""
    FAMILY = "family"
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"
    SCHOOL_BUDDY = "school-buddy"
    WORK_BUDDY = "work-buddy"
    COLLEAGUE = "colleague"

    @staticmethod
    def from_raw(person_relationship_raw: Optional[str]) -> PersonRelationship:
        """Validate and clean a raw person relationship value."""
        if not person_relationship_raw:
            raise ModelValidationError("Expected sync target to be non-null")

        person_relationship_str: str = person_relationship_raw.strip().lower()

        if person_relationship_str not in PersonRelationship.all_values():
            raise ModelValidationError(
                f"Expected sync prefer '{person_relationship_raw}' to be one of '{','.join(PersonRelationship.all_values())}'")

        return PersonRelationship(person_relationship_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for sync targets."""
        return frozenset(st.value for st in PersonRelationship)
