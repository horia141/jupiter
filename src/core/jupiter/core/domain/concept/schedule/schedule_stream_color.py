"""The color of a particular schedule."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class ScheduleStreamColor(EnumValue):
    """The color of a particular schedule stream."""

    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"
    GRAY = "gray"
    BROWN = "brown"
    CYAN = "cyan"
    MAGENTA = "magenta"
