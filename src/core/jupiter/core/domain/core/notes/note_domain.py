"""The source of the note."""


from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class NoteDomain(EnumValue):
    """The source of a note."""

    DOC = "doc"
    INBOX_TASK = "inbox-task"
    METRIC_ENTRY = "metric-entry"
    PERSON = "person"
    LOG = "log"  # for later

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
