from enum import Enum


class SmallScreenHomeTabWidgetPlacementKind(str, Enum):
    SMALL_SCREEN = "small-screen"

    def __str__(self) -> str:
        return str(self.value)
