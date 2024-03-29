"""The source of a calendar event."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class CalendarEventSource(EnumValue):
    """The source of a calendar event."""

    USER = "user"
    PERSON_BIRTHDAY = "person-birthday"
    VACATION = "vacation"

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for a calendar event."""
        return self in (CalendarEventSource.USER,) 
