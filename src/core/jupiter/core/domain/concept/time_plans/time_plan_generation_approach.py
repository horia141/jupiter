"""The approach to generate time plans."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanGenerationApproach(EnumValue):
    """The approach to generate time plans."""

    BOTH_PLAN_AND_TASK = "both-plan-and-task"
    ONLY_PLAN = "only-plan"
    NONE = "none"

    @property
    def should_do_nothing(self) -> bool:
        """Whether to do nothing."""
        return self == TimePlanGenerationApproach.NONE

    @property
    def should_generate_a_time_plan(self) -> bool:
        """Whether to generate a time plan."""
        return (
            self == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK
            or self == TimePlanGenerationApproach.ONLY_PLAN
        )

    @property
    def should_generate_a_planning_task(self) -> bool:
        """Whether to generate a planning task."""
        return self == TimePlanGenerationApproach.BOTH_PLAN_AND_TASK

    @property
    def should_not_generate_a_time_plan(self) -> bool:
        """Whether to not generate a time plan."""
        return self == TimePlanGenerationApproach.NONE

    @property
    def should_not_generate_a_planning_task(self) -> bool:
        """Whether to not generate a planning task."""
        return (
            self == TimePlanGenerationApproach.NONE
            or self == TimePlanGenerationApproach.ONLY_PLAN
        )
