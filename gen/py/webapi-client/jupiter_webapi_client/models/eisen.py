from enum import Enum


class Eisen(str, Enum):
    IMPORTANT = "important"
    IMPORTANT_AND_URGENT = "important-and-urgent"
    REGULAR = "regular"
    URGENT = "urgent"

    def __str__(self) -> str:
        return str(self.value)
