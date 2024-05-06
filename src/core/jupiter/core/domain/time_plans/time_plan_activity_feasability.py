"""The feasability of a particular activity within a plan."""
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanActivityFeasability(EnumValue):
    """The feasability of a particular activity within a plan."""

    MUST_DO = "must-do"
    NICE_TO_HAVE = "nice-to-have"
    STRETCH = "stretch"
