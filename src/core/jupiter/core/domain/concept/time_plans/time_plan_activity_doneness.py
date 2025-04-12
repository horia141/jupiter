"""The doneness of a time plan activity."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanActivityDoneness(EnumValue):
    """The doneness state of a time plan activity."""

    DONE = "done"
    NOT_DONE = "not-done"
    WORKING = "working"
