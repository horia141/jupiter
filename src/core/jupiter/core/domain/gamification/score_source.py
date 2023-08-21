"""The source of a score."""
import enum


@enum.unique
class ScoureSource(enum.Enum):
    """The source of a score."""

    INBOX_TASK = "inbox-task"
    BIG_PLAN = "big-plan"

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
