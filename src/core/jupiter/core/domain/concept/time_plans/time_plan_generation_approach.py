"""The approach to generate time plans."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanGenerationApproach(EnumValue):
    """The approach to generate time plans."""

    BOTH_PLAN_AND_TASK = "both-plan-and-task"
    ONLY_PLAN = "only-plan"
    NONE = "none"
