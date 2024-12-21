from enum import Enum


class ParagraphBlockKind(str, Enum):
    PARAGRAPH = "paragraph"

    def __str__(self) -> str:
        return str(self.value)
