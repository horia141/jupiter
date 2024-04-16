from enum import Enum


class LinkBlockKind(str, Enum):
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
