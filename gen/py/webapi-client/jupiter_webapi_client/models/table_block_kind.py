from enum import Enum


class TableBlockKind(str, Enum):
    TABLE = "table"

    def __str__(self) -> str:
        return str(self.value)
