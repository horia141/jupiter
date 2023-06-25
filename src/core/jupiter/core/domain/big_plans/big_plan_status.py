"""The status of a big plan."""
import enum
from functools import lru_cache, total_ordering
from typing import Iterable, List, Optional, cast

from jupiter.core.framework.errors import InputValidationError


@enum.unique
@total_ordering
class BigPlanStatus(enum.Enum):
    """The status of a big plan."""

    # Created
    NOT_STARTED = "not-started"
    # Accepted
    ACCEPTED = "accepted"
    # Working
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    # Completed
    NOT_DONE = "not-done"
    DONE = "done"

    def to_nice(self) -> str:
        """A prettier version of the value."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def is_accepted(self) -> bool:
        """Whether the status means work has been accepted on the inbox task."""
        return self == BigPlanStatus.ACCEPTED

    @property
    def is_accepted_or_more(self) -> bool:
        """Whether the status means work has been accepted, or is ongoing, or is completed."""
        return self.is_accepted or self.is_working or self.is_completed

    @property
    def is_working(self) -> bool:
        """Whether the status means work is ongoing for the inbox task."""
        return self in (BigPlanStatus.IN_PROGRESS, BigPlanStatus.BLOCKED)

    @property
    def is_working_or_more(self) -> bool:
        """Whether the status means work is ongoing, or is completed."""
        return self.is_working or self.is_completed

    @property
    def is_completed(self) -> bool:
        """Whether the status means work is completed on the inbox task."""
        return self in (BigPlanStatus.NOT_DONE, BigPlanStatus.DONE)

    @staticmethod
    def from_raw(big_plan_status_raw: Optional[str]) -> "BigPlanStatus":
        """Validate and clean the big plan status."""
        if not big_plan_status_raw:
            raise InputValidationError("Expected big plan status to be non-null")

        big_plan_status_str: str = "-".join(
            big_plan_status_raw.strip().lower().split(" "),
        )

        if big_plan_status_str not in BigPlanStatus.all_values():
            raise InputValidationError(
                f"Expected big plan status '{big_plan_status_raw}' to be "
                + f"one of '{','.join(BigPlanStatus.all_values())}'",
            )

        return BigPlanStatus(big_plan_status_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return list(st.value for st in BigPlanStatus)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, BigPlanStatus):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )

        all_values = cast(List[str], self.all_values())

        return all_values.index(self.value) < all_values.index(other.value)

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
