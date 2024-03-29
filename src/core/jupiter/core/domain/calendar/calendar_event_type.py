"""A category for the calendar event."""
from jupiter.core.framework.value import EnumValue, Value, enum_value, value

@enum_value
class CalendarEventType(EnumValue):
    """A category for the calendar event."""

    MULTI_DAY = "multi-day"
    INTRA_DAY = "intra-day"
