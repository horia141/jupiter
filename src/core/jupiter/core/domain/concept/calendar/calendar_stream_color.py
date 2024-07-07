"""The color of a particular calendar."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class CalendarStreamColor(EnumValue):
    """The color of a particular calendar stream."""

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
