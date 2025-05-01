"""A timeline is a construct representing a particular neatly divided unit of time."""

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.timestamp import Timestamp
from pendulum import DateTime


def infer_timeline(period: RecurringTaskPeriod | None, right_now: Timestamp) -> str:
    """Infer the timeline for a recurring task."""
    # Keep sync with the ts:webui:inferPeriodForRecurringTask function
    if period is None:
        return "Lifetime"

    if period == RecurringTaskPeriod.DAILY:
        year = f"{right_now.value.year}"
        quarter = _month_to_quarter(right_now)
        month = _month_to_month(right_now)
        week = f"W{right_now.value.week_of_year}"
        day = f"D{right_now.value.isoweekday()}"

        return f"{year},{quarter},{month},{week},{day}"
    elif period == RecurringTaskPeriod.WEEKLY:
        start_of_week = right_now.value.start_of("week")
        year = f"{start_of_week.year}"
        quarter = _month_to_quarter(start_of_week)
        month = _month_to_month(start_of_week)
        week = f"W{start_of_week.week_of_year}"

        return f"{year},{quarter},{month},{week}"
    elif period == RecurringTaskPeriod.MONTHLY:
        start_of_month = right_now.value.start_of("month")
        year = f"{start_of_month.year}"
        quarter = _month_to_quarter(start_of_month)
        month = _month_to_month(start_of_month)

        return f"{year},{quarter},{month}"
    elif period == RecurringTaskPeriod.QUARTERLY:
        year = f"{right_now.value.year}"
        quarter = _month_to_quarter(right_now)

        return f"{year},{quarter}"
    else:  # period == RecurringTaskPeriod.YEARLY:
        year = f"{right_now.value.year}"

        return year


def _month_to_quarter(date: Timestamp | DateTime) -> str:
    """Map a date to the name of four quarters from the year."""
    month_to_quarter = {
        1: "Q1",
        2: "Q1",
        3: "Q1",
        4: "Q2",
        5: "Q2",
        6: "Q2",
        7: "Q3",
        8: "Q3",
        9: "Q3",
        10: "Q4",
        11: "Q4",
        12: "Q4",
    }

    return month_to_quarter[date.month]


def _month_to_month(date: Timestamp | DateTime) -> str:
    """Map a month to the name it has."""
    month_to_month = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    return month_to_month[date.month]
