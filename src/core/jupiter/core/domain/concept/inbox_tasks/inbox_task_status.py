"""The status of an inbox task."""

from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
@total_ordering
class InboxTaskStatus(EnumValue):
    """The status of an inbox task."""

    # Accepted
    NOT_STARTED = "not-started"
    NOT_STARTED_GEN = "not-started-gen"
    # Working
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    # Completed
    NOT_DONE = "not-done"
    DONE = "done"

    @property
    def is_workable(self) -> bool:
        """Whether the status means the task is not completed."""
        return not self.is_completed

    @property
    def is_not_started(self) -> bool:
        """Whether the status means work has been accepted on the inbox task."""
        return self in (InboxTaskStatus.NOT_STARTED, InboxTaskStatus.NOT_STARTED_GEN)

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

    @staticmethod
    def all_workable_statuses() -> list["InboxTaskStatus"]:
        """All workable statuses."""
        return [s for s in InboxTaskStatus if s.is_workable]

    @staticmethod
    def all_completed_statuses() -> list["InboxTaskStatus"]:
        """All completed statuses."""
        return [s for s in InboxTaskStatus if s.is_completed]
