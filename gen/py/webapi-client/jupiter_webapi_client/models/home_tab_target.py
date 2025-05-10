from enum import Enum


class HomeTabTarget(str, Enum):
    BIG_SCREEN = "big-screen"
    SMALL_SCREEN = "small-screen"

    def __str__(self) -> str:
        return str(self.value)
