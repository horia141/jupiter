from enum import Enum


class CodeBlockKind(str, Enum):
    CODE = "code"

    def __str__(self) -> str:
        return str(self.value)
