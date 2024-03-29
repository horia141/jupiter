"""The source of a calendar."""
from jupiter.core.framework.value import EnumValue, enum_value, value

@enum_value
class CalendarSource(EnumValue):
    """The source of a calendar."""

    USER = "user"
    ICAL_IMPORT = "ical-import"
