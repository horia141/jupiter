from enum import Enum


class TimePlanActivityKind(str, Enum):
    FINISH = "finish"
    MAKE_PROGRESS = "make-progress"

    def __str__(self) -> str:
        return str(self.value)
