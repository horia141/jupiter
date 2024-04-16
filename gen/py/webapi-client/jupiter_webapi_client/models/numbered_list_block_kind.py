from enum import Enum


class NumberedListBlockKind(str, Enum):
    NUMBERED_LIST = "numbered-list"

    def __str__(self) -> str:
        return str(self.value)
