from enum import Enum


class BigScreenHomeTabWidgetPlacementKind(str, Enum):
    BIG_SCREEN = "big-screen"

    def __str__(self) -> str:
        return str(self.value)
