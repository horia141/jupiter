from enum import Enum


class TimePlanSource(str, Enum):
    GENERATED = "generated"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
