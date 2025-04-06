"""The target of an activity."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanActivityTarget(EnumValue):
    """The target of an activity."""

    INBOX_TASK = "inbox-task"
    BIG_PLAN = "big-plan"
