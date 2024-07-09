"""Time event namespace."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimeEventNamespace(EnumValue):
    """Time event namespaces."""

    SCHEDULE_EVENT_IN_DAY = "schedule-event-in-day"
    SCHEDULE_FULL_DAYS_BLOCK = "schedule-full-days-block"
    INBOX_TASK = "inbox-task"
    PERSON_BIRTHDAY = "person-birthday"
