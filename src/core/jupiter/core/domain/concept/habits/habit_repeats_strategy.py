"""The repeat strategy for habits when there are more than one in a period."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class HabitRepeatsStrategy(EnumValue):
    """The repeat strategy for habits when there are more than one in a period."""

    ALL_SAME = "all-same"
    SPREAD_OUT_NO_OVERLAP = "spread-out-no-overlap"

    def spread_tasks(
        self, start_date: ADate, end_date: ADate, repeats_in_period: int
    ) -> list[tuple[ADate, ADate]]:
        """Spread out the tasks as evenly as possible in the period."""
        duration_days = end_date.days_since(start_date) + 1

        if start_date > end_date:
            raise ValueError("The start date must be before the end date")
        if repeats_in_period < 1:
            raise ValueError("The number of repeats in period must be at least 1")
        if duration_days < repeats_in_period:
            raise ValueError(
                "The number of days in the period is less than the repeat count"
            )

        if self == HabitRepeatsStrategy.ALL_SAME:
            return [(start_date, end_date)] * repeats_in_period
        elif self == HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP:
            durations = [0] * repeats_in_period
            day_idx = 0
            for _ in range(duration_days):
                durations[day_idx] += 1
                day_idx = (day_idx + 1) % repeats_in_period
            result = [(start_date, start_date.add_days(durations[0] - 1))]
            for i in range(1, repeats_in_period):
                result.append(
                    (result[-1][1].add_days(1), result[-1][1].add_days(durations[i]))
                )
            return result
