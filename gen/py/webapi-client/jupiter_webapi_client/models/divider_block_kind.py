from enum import Enum


class DividerBlockKind(str, Enum):
    DIVIDER = "divider"

    def __str__(self) -> str:
        return str(self.value)
