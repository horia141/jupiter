from enum import Enum


class ScheduleStreamColor(str, Enum):
    BLUE = "blue"
    BROWN = "brown"
    CYAN = "cyan"
    GRAY = "gray"
    GREEN = "green"
    MAGENTA = "magenta"
    ORANGE = "orange"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"

    def __str__(self) -> str:
        return str(self.value)
