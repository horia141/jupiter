from enum import Enum


class QuoteBlockKind(str, Enum):
    QUOTE = "quote"

    def __str__(self) -> str:
        return str(self.value)
