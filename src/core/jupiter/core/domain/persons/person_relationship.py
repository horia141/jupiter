"""The relationship the user has with a person."""
from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
@total_ordering
class PersonRelationship(EnumValue):
    """The relationship the user has with a person."""

    FAMILY = "family"
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"
    SCHOOL_BUDDY = "school-buddy"
    WORK_BUDDY = "work-buddy"
    COLLEAGUE = "colleague"
    OTHER = "other"

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, PersonRelationship):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)
