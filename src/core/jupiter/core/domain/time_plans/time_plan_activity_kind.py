"""The kind of an activity."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanActivityKind(EnumValue):
    """The kind of a time plan activity."""

    FINISH = "finish"
    MAKE_PROGRESS = "make-progress"
