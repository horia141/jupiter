"""The relationship the user has with a person."""
import enum
from functools import lru_cache, total_ordering
from typing import Optional, Iterable, List, cast

from jupiter.framework.errors import InputValidationError


@enum.unique
@total_ordering
class PersonRelationship(enum.Enum):
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
    def from_raw(person_relationship_raw: Optional[str]) -> "PersonRelationship":
        """Validate and clean a raw person relationship value."""
        if not person_relationship_raw:
            raise InputValidationError("Expected sync target to be non-null")

        person_relationship_str: str = "-".join(
            person_relationship_raw.strip().lower().split()
        )

        if person_relationship_str not in PersonRelationship.all_values():
            raise InputValidationError(
                f"Expected sync prefer '{person_relationship_raw}' to be one of "
                + f"'{','.join(PersonRelationship.all_values())}'"
            )

        return PersonRelationship(person_relationship_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for sync targets."""
        return list(st.value for st in PersonRelationship)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, PersonRelationship):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}"
            )

        all_values = cast(List[str], self.all_values())

        return all_values.index(self.value) < all_values.index(other.value)
