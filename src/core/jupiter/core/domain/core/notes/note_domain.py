"""The source of the note."""
import enum


@enum.unique
class NoteDomain(enum.Enum):
    """The source of a note."""

    DOC = "doc"
    INBOX_TASK = "inbox-task"
    METRIC_ENTRY = "metric-entry"
    PERSON = "person"
    LOG = "log"  # for later

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
