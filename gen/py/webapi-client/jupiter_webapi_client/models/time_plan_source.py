from enum import Enum


class TimePlanSource(str, Enum):
    RECURRING = "recurring"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
