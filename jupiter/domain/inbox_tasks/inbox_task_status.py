"""The status of an inbox task."""
import enum
from functools import lru_cache, total_ordering
from typing import Optional, Iterable, cast, List

from jupiter.framework.errors import InputValidationError


@enum.unique
@total_ordering
class InboxTaskStatus(enum.Enum):
    """The status of an inbox task."""

    # Created
    NOT_STARTED = "not-started"
    # Accepted
    ACCEPTED = "accepted"
    RECURRING = "recurring"
    # Working
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    # Completed
    NOT_DONE = "not-done"
    DONE = "done"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def is_accepted(self) -> bool:
        """Whether the status means work has been accepted on the inbox task."""
        return self in (InboxTaskStatus.ACCEPTED, InboxTaskStatus.RECURRING)

    @property
    def is_accepted_or_more(self) -> bool:
        """Whether the status means work has been accepted, or is ongoing, or is completed."""
        return self.is_accepted or self.is_working or self.is_completed

    @property
    def is_working(self) -> bool:
        """Whether the status means work is ongoing for the inbox task."""
        return self in (InboxTaskStatus.IN_PROGRESS, InboxTaskStatus.BLOCKED)

    @property
    def is_working_or_more(self) -> bool:
        """Whether the status means work is ongoing, or is completed."""
        return self.is_working or self.is_completed

    @property
    def is_completed(self) -> bool:
        """Whether the status means work is completed on the inbox task."""
        return self in (InboxTaskStatus.NOT_DONE, InboxTaskStatus.DONE)

    @staticmethod
    def from_raw(inbox_task_status_raw: Optional[str]) -> "InboxTaskStatus":
        """Validate and clean the big plan status."""
        if not inbox_task_status_raw:
            raise InputValidationError("Expected inbox task status to be non-null")

        inbox_task_status_str: str = "-".join(
            inbox_task_status_raw.strip().lower().split(" ")
        )

        if inbox_task_status_str not in InboxTaskStatus.all_values():
            raise InputValidationError(
                f"Expected inbox task status '{inbox_task_status_raw}' to be "
                + f"one of '{','.join(InboxTaskStatus.all_values())}'"
            )

        return InboxTaskStatus(inbox_task_status_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for inbox tasks."""
        return list(st.value for st in InboxTaskStatus)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, InboxTaskStatus):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}"
            )

        all_values = cast(List[str], self.all_values())

        return all_values.index(self.value) < all_values.index(other.value)

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
