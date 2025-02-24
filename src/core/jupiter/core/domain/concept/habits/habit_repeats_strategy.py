"""The repeat strategy for habits when there are more than one in a period."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class HabitRepeatsStrategy(EnumValue):
    """The repeat strategy for habits when there are more than one in a period."""

    ALL_SAME = "all-same"
    SPREAD_OUT_NO_OVERLAP = "spread-out-no-overlap"

    def spread_tasks(self, repeats_in_period: int) -> list[tuple[ADate, ADate]]:
        pass