from enum import Enum


class TimePlanActivityDoneness(str, Enum):
    DONE = "done"
    NOT_DONE = "not-done"
    WORKING = "working"

    def __str__(self) -> str:
        return str(self.value)
