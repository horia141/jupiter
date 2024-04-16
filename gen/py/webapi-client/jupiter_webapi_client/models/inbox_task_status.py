from enum import Enum


class InboxTaskStatus(str, Enum):
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    DONE = "done"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    NOT_STARTED = "not-started"
    RECURRING = "recurring"

    def __str__(self) -> str:
        return str(self.value)
