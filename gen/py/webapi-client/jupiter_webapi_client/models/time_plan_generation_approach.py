from enum import Enum


class TimePlanGenerationApproach(str, Enum):
    BOTH_PLAN_AND_TASK = "both-plan-and-task"
    NONE = "none"
    ONLY_PLAN = "only-plan"

    def __str__(self) -> str:
        return str(self.value)
