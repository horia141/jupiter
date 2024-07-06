"""Time event namespace."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimeEventNamespace(EnumValue):
    """Time event namespaces."""

    CALENDAR_EVENT = "calendar-event"
    CALENDAR_FULL_DAY_BLOCK = "calendar-full-day-block"
    INBOX_TASK = "inbox-task"
