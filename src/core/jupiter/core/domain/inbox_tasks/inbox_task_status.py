"""The status of an inbox task."""
from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
@total_ordering
class InboxTaskStatus(EnumValue):
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

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, InboxTaskStatus):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)
