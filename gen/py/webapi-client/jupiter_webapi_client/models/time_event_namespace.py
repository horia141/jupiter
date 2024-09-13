from enum import Enum


class TimeEventNamespace(str, Enum):
    INBOX_TASK = "inbox-task"
    PERSON_BIRTHDAY = "person-birthday"
    SCHEDULE_EVENT_IN_DAY = "schedule-event-in-day"
    SCHEDULE_FULL_DAYS_BLOCK = "schedule-full-days-block"
    VACATION = "vacation"

    def __str__(self) -> str:
        return str(self.value)
