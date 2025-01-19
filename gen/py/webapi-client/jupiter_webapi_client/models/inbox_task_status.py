from enum import Enum


class InboxTaskStatus(str, Enum):
    BLOCKED = "blocked"
    DONE = "done"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    NOT_STARTED = "not-started"
    NOT_STARTED_GEN = "not-started-gen"

    def __str__(self) -> str:
        return str(self.value)
