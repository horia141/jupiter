"""A target for a tab."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class HomeTabTarget(EnumValue):
    """A target for a tab."""

    BIG_SCREEN = "big-screen"
    SMALL_SCREEN = "small-screen"
