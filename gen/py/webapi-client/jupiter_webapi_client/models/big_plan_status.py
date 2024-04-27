from enum import Enum


class BigPlanStatus(str, Enum):
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    DONE = "done"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    NOT_STARTED = "not-started"

    def __str__(self) -> str:
        return str(self.value)
