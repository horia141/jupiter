"""The source of a particular calendar."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class CalendarStreamSource(EnumValue):
    """The source of a calendar."""

    USER = "user"
    EXTERNAL_ICAL = "external-ical"
