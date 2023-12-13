"""The source of the note."""
import enum


@enum.unique
class NoteSource(enum.Enum):
    """The source of a note."""

    USER = "user"
    METRIC_ENTRY = "metric-entry"
    PERSON = "person"
    LOG = "log"  # for later

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
