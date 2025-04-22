from enum import Enum


class InboxTaskSource(str, Enum):
    BIG_PLAN = "big-plan"
    CHORE = "chore"
    EMAIL_TASK = "email-task"
    HABIT = "habit"
    JOURNAL = "journal"
    METRIC = "metric"
    PERSON_BIRTHDAY = "person-birthday"
    PERSON_CATCH_UP = "person-catch-up"
    SLACK_TASK = "slack-task"
    TIME_PLAN = "time-plan"
    USER = "user"
    WORKING_MEM_CLEANUP = "working-mem-cleanup"

    def __str__(self) -> str:
        return str(self.value)
