"""The rules for skipping a recurring task."""
from typing import Literal, cast

import pendulum
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)
from pendulum.date import Date


@value
class RecurringTaskSkipRule(AtomicValue[str]):
    """The rules for skipping a recurring task."""

    the_type: Literal[
        "even",
        "odd",
        "every",
        "custom_daily_rel_weekly",
        "custom_daily_rel_monthly",
        "custom_weekly_rel_yearly",
        "custom_monthly_rel_yearly",
        "custom_quarterly_rel_yearly",
    ]
    every_n_k: tuple[int, int] | None
    custom_daily_rel_weekly: list[int] | None
    custom_daily_rel_monthly: list[int] | None
    custom_weekly_rel_yearly: list[int] | None
    custom_monthly_rel_yearly: list[int] | None
    custom_quarterly_rel_yearly: list[int] | None

    @staticmethod
    def do_even() -> "RecurringTaskSkipRule":
        """Skip even days."""
        return RecurringTaskSkipRule(
            the_type="even",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_odd() -> "RecurringTaskSkipRule":
        """Skip odd days."""
        return RecurringTaskSkipRule(
            the_type="odd",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_every_n_k(n: int, k: int) -> "RecurringTaskSkipRule":
        """Construct a skip rule that skips every n days shifting by k."""
        return RecurringTaskSkipRule(
            the_type="every",
            every_n_k=(n, k),
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_custom_daily_rel_weekly(days: list[int]) -> "RecurringTaskSkipRule":
        """Skip custom days in a week."""
        return RecurringTaskSkipRule(
            the_type="custom_daily_rel_weekly",
            every_n_k=None,
            custom_daily_rel_weekly=days,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_custom_daily_rel_monthly(days: list[int]) -> "RecurringTaskSkipRule":
        """Skip custom days in a month."""
        return RecurringTaskSkipRule(
            the_type="custom_daily_rel_monthly",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=days,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_custom_weekly_rel_yearly(weeks: list[int]) -> "RecurringTaskSkipRule":
        """Skip custom weeks in a month."""
        return RecurringTaskSkipRule(
            the_type="custom_weekly_rel_yearly",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=weeks,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_custom_monthly_rel_yearly(months: list[int]) -> "RecurringTaskSkipRule":
        """Skip custom months in a year."""
        return RecurringTaskSkipRule(
            the_type="custom_monthly_rel_yearly",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=months,
            custom_quarterly_rel_yearly=None,
        )

    @staticmethod
    def do_custom_quarterly_rel_yearly(quarters: list[int]) -> "RecurringTaskSkipRule":
        """Skip custom quarters in a year."""
        return RecurringTaskSkipRule(
            the_type="custom_quarterly_rel_yearly",
            every_n_k=None,
            custom_daily_rel_weekly=None,
            custom_daily_rel_monthly=None,
            custom_weekly_rel_yearly=None,
            custom_monthly_rel_yearly=None,
            custom_quarterly_rel_yearly=quarters,
        )

    def is_compatible_with(self, period: RecurringTaskPeriod) -> bool:
        if period == RecurringTaskPeriod.DAILY:
            return self.the_type in [
                "even",
                "odd",
                "every",
                "custom_daily_rel_weekly",
                "custom_daily_rel_monthly",
            ]
        elif period == RecurringTaskPeriod.WEEKLY:
            return self.the_type in ["even", "odd", "every", "custom_weekly_rel_yearly"]
        elif period == RecurringTaskPeriod.MONTHLY:
            return self.the_type in [
                "even",
                "odd",
                "every",
                "custom_monthly_rel_yearly",
            ]
        elif period == RecurringTaskPeriod.QUARTERLY:
            return self.the_type in [
                "even",
                "odd",
                "every",
                "custom_quarterly_rel_yearly",
            ]
        else:
            return self.the_type in ["even", "odd", "every"]

    def should_keep(self, period: RecurringTaskPeriod, date: Date) -> bool:
        """Apply the skip rule to a date."""
        epoch_date = pendulum.from_timestamp(0).date()
        if period == RecurringTaskPeriod.DAILY:
            days_since_epoch = date.diff(epoch_date).in_days()
            if self.the_type == "even":
                return days_since_epoch % 2 == 0
            elif self.the_type == "odd":
                return days_since_epoch % 2 != 0
            elif self.the_type == "every":
                n, k = cast(tuple[int, int], self.every_n_k)
                return days_since_epoch % n == k
            elif self.the_type == "custom_daily_rel_weekly":
                return date.isoweekday() in cast(
                    list[int], self.custom_daily_rel_weekly
                )
            elif self.the_type == "custom_daily_rel_monthly":
                return date.day in cast(list[int], self.custom_daily_rel_monthly)
            else:
                return False
        elif period == RecurringTaskPeriod.WEEKLY:
            if self.the_type == "even":
                return date.week_of_year % 2 == 0
            elif self.the_type == "odd":
                return date.week_of_year % 2 != 0
            elif self.the_type == "every":
                n, k = cast(tuple[int, int], self.every_n_k)
                return date.week_of_year % n == k
            elif self.the_type == "custom_weekly_rel_yearly":
                return date.week_of_year in cast(
                    list[int], self.custom_weekly_rel_yearly
                )
            else:
                return False
        elif period == RecurringTaskPeriod.MONTHLY:
            if self.the_type == "even":
                return date.month % 2 == 0
            elif self.the_type == "odd":
                return date.month % 2 != 0
            elif self.the_type == "every":
                n, k = cast(tuple[int, int], self.every_n_k)
                return date.month % n == k
            elif self.the_type == "custom_monthly_rel_yearly":
                return date.month in cast(list[int], self.custom_monthly_rel_yearly)
            else:
                return False
        elif period == RecurringTaskPeriod.QUARTERLY:
            if self.the_type == "even":
                return date.quarter % 2 == 0
            elif self.the_type == "odd":
                return date.quarter % 2 != 0
            elif self.the_type == "every":
                n, k = cast(tuple[int, int], self.every_n_k)
                return date.quarter % n == k
            elif self.the_type == "custom_quarterly_rel_yearly":
                return date.quarter in cast(list[int], self.custom_quarterly_rel_yearly)
            else:
                return False
        else:
            if self.the_type == "even":
                return date.year % 2 == 0
            elif self.the_type == "odd":
                return date.year % 2 != 0
            elif self.the_type == "every":
                n, k = cast(tuple[int, int], self.every_n_k)
                return date.year % n == k
            else:
                return False

    def _validate(self) -> None:
        if self.the_type == "even":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
        elif self.the_type == "odd":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
        elif self.the_type == "every":
            if self.every_n_k is None:
                raise InputValidationError("every_n_k must be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
            n, k = cast(tuple[int, int], self.every_n_k)
            if n < 1:
                raise InputValidationError("n must be non-negative")
            if k < 0:
                raise InputValidationError("k must be non-negative")
            if k >= n:
                raise InputValidationError("k must be less than n")
        elif self.the_type == "custom_daily_rel_weekly":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is None:
                raise InputValidationError("custom_daily_rel_weekly must be specified")
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
            days = cast(list[int], self.custom_daily_rel_weekly)
            if len(days) == 0:
                raise InputValidationError("At least one day must be specified")
            if len(days) > 7:
                raise InputValidationError("At most 7 days can be specified")
            if any(day < 1 or day > 7 for day in days):
                raise InputValidationError("Days must be between 1 and 7")
        elif self.the_type == "custom_daily_rel_monthly":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is None:
                raise InputValidationError("custom_daily_rel_monthly must be specified")
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
            days = cast(list[int], self.custom_daily_rel_monthly)
            if len(days) == 0:
                raise InputValidationError("At least one day must be specified")
            if len(days) > 31:
                raise InputValidationError("At most 31 days can be specified")
            if any(day < 1 or day > 31 for day in days):
                raise InputValidationError("Days must be between 1 and 31")
        elif self.the_type == "custom_weekly_rel_yearly":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is None:
                raise InputValidationError("custom_weekly_rel_yearly must be specified")
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
            weeks = cast(list[int], self.custom_weekly_rel_yearly)
            if len(weeks) == 0:
                raise InputValidationError("At least one week must be specified")
            if len(weeks) > 52:
                raise InputValidationError("At most 5 weeks can be specified")
            if any(week < 1 or week > 52 for week in weeks):
                raise InputValidationError("Weeks must be between 1 and 52")
        elif self.the_type == "custom_monthly_rel_yearly":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must be specified"
                )
            if self.custom_quarterly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must not be specified"
                )
            months = cast(list[int], self.custom_monthly_rel_yearly)
            if len(months) == 0:
                raise InputValidationError("At least one month must be specified")
            if len(months) > 12:
                raise InputValidationError("At most 12 months can be specified")
            if any(month < 1 or month > 12 for month in months):
                raise InputValidationError("Months must be between 1 and 12")
        elif self.the_type == "custom_quarterly_rel_yearly":
            if self.every_n_k is not None:
                raise InputValidationError("every_n_k must not be specified")
            if self.custom_daily_rel_weekly is not None:
                raise InputValidationError(
                    "custom_daily_rel_weekly must not be specified"
                )
            if self.custom_daily_rel_monthly is not None:
                raise InputValidationError(
                    "custom_daily_rel_monthly must not be specified"
                )
            if self.custom_weekly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_weekly_rel_yearly must not be specified"
                )
            if self.custom_monthly_rel_yearly is not None:
                raise InputValidationError(
                    "custom_monthly_rel_yearly must not be specified"
                )
            if self.custom_quarterly_rel_yearly is None:
                raise InputValidationError(
                    "custom_quarterly_rel_yearly must be specified"
                )
            quarters = cast(list[int], self.custom_quarterly_rel_yearly)
            if len(quarters) == 0:
                raise InputValidationError("At least one quarter must be specified")
            if len(quarters) > 4:
                raise InputValidationError("At most 4 quarters can be specified")
            if any(quarter < 1 or quarter > 4 for quarter in quarters):
                raise InputValidationError("Quarters must be between 1 and 4")
        else:
            raise InputValidationError(f"Invalid skip rule type {self.the_type}")

    def __str__(self) -> str:
        """Transform this to a string version."""
        if self.the_type == "even":
            return "even"
        elif self.the_type == "odd":
            return "odd"
        elif self.the_type == "every":
            n, k = cast(tuple[int, int], self.every_n_k)
            return f"every {n} times, starting from {k}"
        elif self.the_type == "custom_daily_rel_weekly":
            return f"custom daily relative to weekly: {self.custom_daily_rel_weekly}"
        elif self.the_type == "custom_daily_rel_monthly":
            return f"custom daily relative to monthly: {self.custom_daily_rel_monthly}"
        elif self.the_type == "custom_weekly_rel_yearly":
            return f"custom weekly relative to yearly: {self.custom_weekly_rel_yearly}"
        elif self.the_type == "custom_monthly_rel_yearly":
            return (
                f"custom monthly relative to yearly: {self.custom_monthly_rel_yearly}"
            )
        elif self.the_type == "custom_quarterly_rel_yearly":
            return f"custom quarterly relative to yearly: {self.custom_quarterly_rel_yearly}"


class RecurringTaskSkipRuleDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[RecurringTaskSkipRule]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: RecurringTaskSkipRule) -> Primitive:
        """Encode to a primtiive."""
        if value.the_type == "even":
            return "even"
        elif value.the_type == "odd":
            return "odd"
        elif value.the_type == "every":
            n, k = cast(tuple[int, int], value.every_n_k)
            return f"every {n} {k}"
        elif value.the_type == "custom_daily_rel_weekly":
            return f"custom_daily_rel_weekly {' '.join(str(day) for day in cast(list[int], value.custom_daily_rel_weekly))}"
        elif value.the_type == "custom_daily_rel_monthly":
            return f"custom_daily_rel_monthly {' '.join(str(day) for day in cast(list[int], value.custom_daily_rel_monthly))}"
        elif value.the_type == "custom_weekly_rel_yearly":
            return f"custom_weekly_rel_yearly {' '.join(str(week) for week in cast(list[int], value.custom_weekly_rel_yearly))}"
        elif value.the_type == "custom_monthly_rel_yearly":
            return f"custom_monthly_rel_yearly {' '.join(str(month) for month in cast(list[int], value.custom_monthly_rel_yearly))}"
        elif value.the_type == "custom_quarterly_rel_yearly":
            return f"custom_quarterly_rel_yearly {' '.join(str(quarter) for quarter in cast(list[int], value.custom_quarterly_rel_yearly))}"


class RecurringTaskSkipRuleDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[RecurringTaskSkipRule]
):
    """Decode from a database primitive."""

    def from_raw_str(self, primitive: str) -> RecurringTaskSkipRule:
        """Decode from a raw string."""
        parts = primitive.strip().split(" ")
        if len(parts) == 1:
            if parts[0] == "even":
                return RecurringTaskSkipRule.do_even()
            elif parts[0] == "odd":
                return RecurringTaskSkipRule.do_odd()
            else:
                raise InputValidationError(
                    f"Invalid format for skip rule '{primitive}'"
                )
        elif len(parts) >= 2:
            if parts[0] == "every":
                if len(parts) != 3:
                    raise InputValidationError(
                        f"Invalid format for skip rule '{primitive}'"
                    )
                try:
                    n = int(parts[1], base=10)
                    k = int(parts[2], base=10)
                    return RecurringTaskSkipRule.do_every_n_k(n, k)
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid n or k value in '{primitive}'"
                    ) from err
            elif parts[0] == "custom_daily_rel_weekly":
                try:
                    days = [int(day, base=10) for day in parts[1:]]
                    return RecurringTaskSkipRule.do_custom_daily_rel_weekly(days)
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid day value in '{primitive}'"
                    ) from err
            elif parts[0] == "custom_daily_rel_monthly":
                try:
                    days = [int(day, base=10) for day in parts[1:]]
                    return RecurringTaskSkipRule.do_custom_daily_rel_monthly(days)
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid day value in '{primitive}'"
                    ) from err
            elif parts[0] == "custom_weekly_rel_yearly":
                try:
                    weeks = [int(week, base=10) for week in parts[1:]]
                    return RecurringTaskSkipRule.do_custom_weekly_rel_yearly(weeks)
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid week value in '{primitive}'"
                    ) from err
            elif parts[0] == "custom_monthly_rel_yearly":
                try:
                    months = [int(month, base=10) for month in parts[1:]]
                    return RecurringTaskSkipRule.do_custom_monthly_rel_yearly(months)
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid month value in '{primitive}'"
                    ) from err
            elif parts[0] == "custom_quarterly_rel_yearly":
                try:
                    quarters = [int(quarter, base=10) for quarter in parts[1:]]
                    return RecurringTaskSkipRule.do_custom_quarterly_rel_yearly(
                        quarters
                    )
                except ValueError as err:
                    raise InputValidationError(
                        f"Invalid quarter value in '{primitive}'"
                    ) from err
            else:
                raise InputValidationError(
                    f"Invalid format for skip rule '{primitive}'"
                )
        else:
            raise InputValidationError(f"Invalid format for skip rule '{primitive}'")
