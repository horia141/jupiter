from enum import Enum


class HeadingBlockKind(str, Enum):
    HEADING = "heading"

    def __str__(self) -> str:
        return str(self.value)
