from enum import Enum


class ScoreSource(str, Enum):
    BIG_PLAN = "big-plan"
    INBOX_TASK = "inbox-task"

    def __str__(self) -> str:
        return str(self.value)
