from enum import Enum


class ScheduleSource(str, Enum):
    EXTERNAL_ICAL = "external-ical"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
