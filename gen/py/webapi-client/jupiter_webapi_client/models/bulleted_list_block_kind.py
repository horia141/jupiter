from enum import Enum


class BulletedListBlockKind(str, Enum):
    BULLETED_LIST = "bulleted-list"

    def __str__(self) -> str:
        return str(self.value)
