"""Tests for the recurring task skip rule."""
import pendulum
import pytest
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import (
    RecurringTaskSkipRule,
    RecurringTaskSkipRuleDatabaseDecoder,
    RecurringTaskSkipRuleDatabaseEncoder,
)
from jupiter.core.framework.errors import InputValidationError

PERIOD_COMPATIBILITY = [
    (RecurringTaskPeriod.DAILY, RecurringTaskSkipRule.do_even(), True),
    (RecurringTaskPeriod.DAILY, RecurringTaskSkipRule.do_odd(), True),
    (RecurringTaskPeriod.DAILY, RecurringTaskSkipRule.do_every_n_k(1, 0), True),
    (
        RecurringTaskPeriod.DAILY,
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1]),
        True,
    ),
    (
        RecurringTaskPeriod.DAILY,
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1]),
        True,
    ),
    (
        RecurringTaskPeriod.DAILY,
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.DAILY,
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.DAILY,
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1]),
        False,
    ),
    (RecurringTaskPeriod.WEEKLY, RecurringTaskSkipRule.do_even(), True),
    (RecurringTaskPeriod.WEEKLY, RecurringTaskSkipRule.do_odd(), True),
    (RecurringTaskPeriod.WEEKLY, RecurringTaskSkipRule.do_every_n_k(1, 0), True),
    (
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1]),
        True,
    ),
    (
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1]),
        False,
    ),
    (RecurringTaskPeriod.MONTHLY, RecurringTaskSkipRule.do_even(), True),
    (RecurringTaskPeriod.MONTHLY, RecurringTaskSkipRule.do_odd(), True),
    (RecurringTaskPeriod.MONTHLY, RecurringTaskSkipRule.do_every_n_k(1, 0), True),
    (
        RecurringTaskPeriod.MONTHLY,
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.MONTHLY,
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.MONTHLY,
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.MONTHLY,
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1]),
        True,
    ),
    (
        RecurringTaskPeriod.MONTHLY,
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1]),
        False,
    ),
    (RecurringTaskPeriod.QUARTERLY, RecurringTaskSkipRule.do_even(), True),
    (RecurringTaskPeriod.QUARTERLY, RecurringTaskSkipRule.do_odd(), True),
    (RecurringTaskPeriod.QUARTERLY, RecurringTaskSkipRule.do_every_n_k(1, 0), True),
    (
        RecurringTaskPeriod.QUARTERLY,
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.QUARTERLY,
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.QUARTERLY,
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.QUARTERLY,
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.QUARTERLY,
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1]),
        True,
    ),
    (RecurringTaskPeriod.YEARLY, RecurringTaskSkipRule.do_even(), True),
    (RecurringTaskPeriod.YEARLY, RecurringTaskSkipRule.do_odd(), True),
    (RecurringTaskPeriod.YEARLY, RecurringTaskSkipRule.do_every_n_k(1, 0), True),
    (
        RecurringTaskPeriod.YEARLY,
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.YEARLY,
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.YEARLY,
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.YEARLY,
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1]),
        False,
    ),
    (
        RecurringTaskPeriod.YEARLY,
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1]),
        False,
    ),
]


@pytest.mark.parametrize(("period", "rule", "is_compatible"), PERIOD_COMPATIBILITY)
def test_is_compatible_with(
    period: RecurringTaskPeriod, rule: RecurringTaskSkipRule, is_compatible: bool
) -> None:
    assert rule.is_compatible_with(period) == is_compatible


TEST_DAYS = [pendulum.date(2024, 12, 1).add(days=i) for i in range(31 + 31)]
TEST_WEEKS = [pendulum.date(2024, 12, 1).add(weeks=i) for i in range(10)]
TEST_MONTHS = [pendulum.date(2024, 1, 1).add(months=i) for i in range(12)]
TEST_QUARTERS = [pendulum.date(2024, 1, 1).add(months=i * 3) for i in range(4)]
TEST_YEARS = [pendulum.date(2024, 1, 1).add(years=i) for i in range(10)]


@pytest.mark.parametrize(
    ("day", "should_keep"), [(day, i % 2 == 0) for i, day in enumerate(TEST_DAYS)]
)
def test_do_even_daily(day: pendulum.Date, should_keep: bool) -> None:
    do_even = RecurringTaskSkipRule.do_even()
    assert do_even.should_keep(RecurringTaskPeriod.DAILY, day) == should_keep


@pytest.mark.parametrize(
    ("day", "should_keep"), [(day, i % 2 == 1) for i, day in enumerate(TEST_DAYS)]
)
def test_do_odd_daily(day: pendulum.Date, should_keep: bool) -> None:
    do_odd = RecurringTaskSkipRule.do_odd()
    assert do_odd.should_keep(RecurringTaskPeriod.DAILY, day) == should_keep


@pytest.mark.parametrize(
    ("day", "should_keep"), [(day, i % 3 == 0) for i, day in enumerate(TEST_DAYS)]
)
def test_do_every_3_0_daily(day: pendulum.Date, should_keep: bool) -> None:
    do_every_3_0 = RecurringTaskSkipRule.do_every_n_k(3, 0)
    assert do_every_3_0.should_keep(RecurringTaskPeriod.DAILY, day) == should_keep


@pytest.mark.parametrize(
    ("day", "should_keep"), [(day, (i + 3) % 5 == 2) for i, day in enumerate(TEST_DAYS)]
)
def test_do_every_5_2_daily(day: pendulum.Date, should_keep: bool) -> None:
    do_every_5_2 = RecurringTaskSkipRule.do_every_n_k(5, 2)
    assert do_every_5_2.should_keep(RecurringTaskPeriod.DAILY, day) == should_keep


@pytest.mark.parametrize(
    ("day", "should_keep"),
    [
        (day, day.format("dddd") == "Monday" or day.format("dddd") == "Thursday")
        for i, day in enumerate(TEST_DAYS)
    ],
)
def test_do_custom_daily_rel_weekly_daily(
    day: pendulum.Date, should_keep: bool
) -> None:
    do_custom_daily_rel_weekly = RecurringTaskSkipRule.do_custom_daily_rel_weekly(
        [1, 4]
    )
    assert (
        do_custom_daily_rel_weekly.should_keep(RecurringTaskPeriod.DAILY, day)
        == should_keep
    )


@pytest.mark.parametrize(
    ("day", "should_keep"),
    [
        (day, day.day == 1 or day.day == 15 or day.day == 28)
        for i, day in enumerate(TEST_DAYS)
    ],
)
def test_do_custom_daily_rel_monthly_daily(
    day: pendulum.Date, should_keep: bool
) -> None:
    do_custom_daily_rel_monthly = RecurringTaskSkipRule.do_custom_daily_rel_monthly(
        [1, 15, 28]
    )
    assert (
        do_custom_daily_rel_monthly.should_keep(RecurringTaskPeriod.DAILY, day)
        == should_keep
    )


@pytest.mark.parametrize(
    ("week", "should_keep"),
    [(week, week.week_of_year % 2 == 0) for i, week in enumerate(TEST_WEEKS)],
)
def test_do_even_weekly(week: pendulum.Date, should_keep: bool) -> None:
    do_even = RecurringTaskSkipRule.do_even()
    assert do_even.should_keep(RecurringTaskPeriod.WEEKLY, week) == should_keep


@pytest.mark.parametrize(
    ("week", "should_keep"),
    [(week, week.week_of_year % 2 == 1) for i, week in enumerate(TEST_WEEKS)],
)
def test_do_odd_weekly(week: pendulum.Date, should_keep: bool) -> None:
    do_odd = RecurringTaskSkipRule.do_odd()
    assert do_odd.should_keep(RecurringTaskPeriod.WEEKLY, week) == should_keep


@pytest.mark.parametrize(
    ("week", "should_keep"),
    [(week, week.week_of_year % 3 == 0) for i, week in enumerate(TEST_WEEKS)],
)
def test_do_every_3_0_weekly(week: pendulum.Date, should_keep: bool) -> None:
    do_every_3_0 = RecurringTaskSkipRule.do_every_n_k(3, 0)
    assert do_every_3_0.should_keep(RecurringTaskPeriod.WEEKLY, week) == should_keep


@pytest.mark.parametrize(
    ("week", "should_keep"),
    [(week, week.week_of_year % 5 == 2) for i, week in enumerate(TEST_WEEKS)],
)
def test_do_every_5_2_weekly(week: pendulum.Date, should_keep: bool) -> None:
    do_every_5_2 = RecurringTaskSkipRule.do_every_n_k(5, 2)
    assert do_every_5_2.should_keep(RecurringTaskPeriod.WEEKLY, week) == should_keep


@pytest.mark.parametrize(
    ("week", "should_keep"),
    [
        (
            week,
            week.week_of_year == 1
            or week.week_of_year == 26
            or week.week_of_year == 52,
        )
        for i, week in enumerate(TEST_WEEKS)
    ],
)
def test_do_custom_weekly_rel_yearly_weekly(
    week: pendulum.Date, should_keep: bool
) -> None:
    do_custom_weekly_rel_yearly = RecurringTaskSkipRule.do_custom_weekly_rel_yearly(
        [1, 26, 52]
    )
    assert (
        do_custom_weekly_rel_yearly.should_keep(RecurringTaskPeriod.WEEKLY, week)
        == should_keep
    )


@pytest.mark.parametrize(
    ("month", "should_keep"),
    [(month, month.month % 2 == 0) for i, month in enumerate(TEST_MONTHS)],
)
def test_do_even_monthly(month: pendulum.Date, should_keep: bool) -> None:
    do_even = RecurringTaskSkipRule.do_even()
    assert do_even.should_keep(RecurringTaskPeriod.MONTHLY, month) == should_keep


@pytest.mark.parametrize(
    ("month", "should_keep"),
    [(month, month.month % 2 == 1) for i, month in enumerate(TEST_MONTHS)],
)
def test_do_odd_monthly(month: pendulum.Date, should_keep: bool) -> None:
    do_odd = RecurringTaskSkipRule.do_odd()
    assert do_odd.should_keep(RecurringTaskPeriod.MONTHLY, month) == should_keep


@pytest.mark.parametrize(
    ("month", "should_keep"),
    [(month, month.month % 3 == 0) for i, month in enumerate(TEST_MONTHS)],
)
def test_do_every_3_0_monthly(month: pendulum.Date, should_keep: bool) -> None:
    do_every_3_0 = RecurringTaskSkipRule.do_every_n_k(3, 0)
    assert do_every_3_0.should_keep(RecurringTaskPeriod.MONTHLY, month) == should_keep


@pytest.mark.parametrize(
    ("month", "should_keep"),
    [(month, month.month % 5 == 2) for i, month in enumerate(TEST_MONTHS)],
)
def test_do_every_5_2_monthly(month: pendulum.Date, should_keep: bool) -> None:
    do_every_5_2 = RecurringTaskSkipRule.do_every_n_k(5, 2)
    assert do_every_5_2.should_keep(RecurringTaskPeriod.MONTHLY, month) == should_keep


@pytest.mark.parametrize(
    ("month", "should_keep"),
    [
        (
            month,
            month.format("MMMM") == "January"
            or month.format("MMMM") == "June"
            or month.format("MMMM") == "December",
        )
        for i, month in enumerate(TEST_MONTHS)
    ],
)
def test_do_custom_monthly_rel_yearly_monthly(
    month: pendulum.Date, should_keep: bool
) -> None:
    do_custom_monthly_rel_yearly = RecurringTaskSkipRule.do_custom_monthly_rel_yearly(
        [1, 6, 12]
    )
    assert (
        do_custom_monthly_rel_yearly.should_keep(RecurringTaskPeriod.MONTHLY, month)
        == should_keep
    )


@pytest.mark.parametrize(
    ("quarter", "should_keep"),
    [(quarter, quarter.quarter % 2 == 0) for i, quarter in enumerate(TEST_QUARTERS)],
)
def test_do_even_quarterly(quarter: pendulum.Date, should_keep: bool) -> None:
    do_even = RecurringTaskSkipRule.do_even()
    assert do_even.should_keep(RecurringTaskPeriod.QUARTERLY, quarter) == should_keep


@pytest.mark.parametrize(
    ("quarter", "should_keep"),
    [(quarter, quarter.quarter % 2 == 1) for i, quarter in enumerate(TEST_QUARTERS)],
)
def test_do_odd_quarterly(quarter: pendulum.Date, should_keep: bool) -> None:
    do_odd = RecurringTaskSkipRule.do_odd()
    assert do_odd.should_keep(RecurringTaskPeriod.QUARTERLY, quarter) == should_keep


@pytest.mark.parametrize(
    ("quarter", "should_keep"),
    [(quarter, quarter.quarter % 3 == 0) for i, quarter in enumerate(TEST_QUARTERS)],
)
def test_do_every_3_0_quarterly(quarter: pendulum.Date, should_keep: bool) -> None:
    do_every_3_0 = RecurringTaskSkipRule.do_every_n_k(3, 0)
    assert (
        do_every_3_0.should_keep(RecurringTaskPeriod.QUARTERLY, quarter) == should_keep
    )


@pytest.mark.parametrize(
    ("quarter", "should_keep"),
    [(quarter, quarter.quarter % 5 == 2) for i, quarter in enumerate(TEST_QUARTERS)],
)
def test_do_every_5_2_quarterly(quarter: pendulum.Date, should_keep: bool) -> None:
    do_every_5_2 = RecurringTaskSkipRule.do_every_n_k(5, 2)
    assert (
        do_every_5_2.should_keep(RecurringTaskPeriod.QUARTERLY, quarter) == should_keep
    )


@pytest.mark.parametrize(
    ("quarter", "should_keep"),
    [
        (quarter, quarter.quarter == 1 or quarter.quarter == 2 or quarter.quarter == 3)
        for i, quarter in enumerate(TEST_QUARTERS)
    ],
)
def test_do_custom_quarterly_rel_yearly_quarterly(
    quarter: pendulum.Date, should_keep: bool
) -> None:
    do_custom_quarterly_rel_yearly = (
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1, 2, 3])
    )
    assert (
        do_custom_quarterly_rel_yearly.should_keep(
            RecurringTaskPeriod.QUARTERLY, quarter
        )
        == should_keep
    )


@pytest.mark.parametrize(
    ("year", "should_keep"),
    [(year, year.year % 2 == 0) for i, year in enumerate(TEST_YEARS)],
)
def test_do_even_yearly(year: pendulum.Date, should_keep: bool) -> None:
    do_even = RecurringTaskSkipRule.do_even()
    assert do_even.should_keep(RecurringTaskPeriod.YEARLY, year) == should_keep


@pytest.mark.parametrize(
    ("year", "should_keep"),
    [(year, year.year % 2 == 1) for i, year in enumerate(TEST_YEARS)],
)
def test_do_odd_yearly(year: pendulum.Date, should_keep: bool) -> None:
    do_odd = RecurringTaskSkipRule.do_odd()
    assert do_odd.should_keep(RecurringTaskPeriod.YEARLY, year) == should_keep


@pytest.mark.parametrize(
    ("year", "should_keep"),
    [(year, year.year % 3 == 0) for i, year in enumerate(TEST_YEARS)],
)
def test_do_every_3_0_yearly(year: pendulum.Date, should_keep: bool) -> None:
    do_every_3_0 = RecurringTaskSkipRule.do_every_n_k(3, 0)
    assert do_every_3_0.should_keep(RecurringTaskPeriod.YEARLY, year) == should_keep


@pytest.mark.parametrize(
    ("year", "should_keep"),
    [(year, year.year % 5 == 2) for i, year in enumerate(TEST_YEARS)],
)
def test_do_every_5_2_yearly(year: pendulum.Date, should_keep: bool) -> None:
    do_every_5_2 = RecurringTaskSkipRule.do_every_n_k(5, 2)
    assert do_every_5_2.should_keep(RecurringTaskPeriod.YEARLY, year) == should_keep


STRING_FORMS = [
    (RecurringTaskSkipRule.do_even(), "even"),
    (RecurringTaskSkipRule.do_odd(), "odd"),
    (RecurringTaskSkipRule.do_every_n_k(3, 0), "every 3 times, starting from 0"),
    (RecurringTaskSkipRule.do_every_n_k(5, 2), "every 5 times, starting from 2"),
    (
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1, 4]),
        "custom daily relative to weekly: [1, 4]",
    ),
    (
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1, 15, 28]),
        "custom daily relative to monthly: [1, 15, 28]",
    ),
    (
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1, 26, 52]),
        "custom weekly relative to yearly: [1, 26, 52]",
    ),
    (
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1, 6, 12]),
        "custom monthly relative to yearly: [1, 6, 12]",
    ),
    (
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1, 2, 3]),
        "custom quarterly relative to yearly: [1, 2, 3]",
    ),
]


@pytest.mark.parametrize(("rule", "string_form"), STRING_FORMS)
def test_string_form(rule: RecurringTaskSkipRule, string_form: str) -> None:
    assert str(rule) == string_form


INVALID_CONSTRUCTIONS = [
    (RecurringTaskSkipRule.do_every_n_k, -1, 0),
    (RecurringTaskSkipRule.do_every_n_k, 4, -1),
    (RecurringTaskSkipRule.do_every_n_k, 4, 4),
    (RecurringTaskSkipRule.do_custom_daily_rel_weekly, []),
    (RecurringTaskSkipRule.do_custom_daily_rel_weekly, [1, 2, 3, 4, 5, 6, 7, 7]),
    (RecurringTaskSkipRule.do_custom_daily_rel_weekly, [-1]),
    (RecurringTaskSkipRule.do_custom_daily_rel_weekly, [8]),
    (RecurringTaskSkipRule.do_custom_daily_rel_monthly, []),
    (RecurringTaskSkipRule.do_custom_daily_rel_monthly, [1] * 32),
    (RecurringTaskSkipRule.do_custom_daily_rel_monthly, [-1]),
    (RecurringTaskSkipRule.do_custom_daily_rel_monthly, [32]),
]


@pytest.mark.parametrize("constructor", INVALID_CONSTRUCTIONS)
def test_invalid_constructions(constructor) -> None:  # type: ignore
    with pytest.raises(InputValidationError):
        constructor[0](*constructor[1:])


INVALID_STRUCTURES = [
    {
        "the_type": "even",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "even",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "even",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "even",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "even",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "even",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "odd",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "odd",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "odd",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "odd",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "odd",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "odd",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "every_n_k",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "every_n_k",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "every_n_k",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "every_n_k",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "every_n_k",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "every_n_k",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_weekly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_daily_rel_monthly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_weekly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_monthly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": None,
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": (3, 2),
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": [1],
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": [1],
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": [1],
        "custom_monthly_rel_yearly": None,
        "custom_quarterly_rel_yearly": [1],
    },
    {
        "the_type": "custom_quarterly_rel_yearly",
        "every_n_k": None,
        "custom_daily_rel_weekly": None,
        "custom_daily_rel_monthly": None,
        "custom_weekly_rel_yearly": None,
        "custom_monthly_rel_yearly": [1],
        "custom_quarterly_rel_yearly": [1],
    },
]


@pytest.mark.parametrize("structure", INVALID_STRUCTURES)
def test_invalid_structures(structure) -> None:  # type: ignore
    with pytest.raises(InputValidationError):
        RecurringTaskSkipRule(**structure)


DATABASE_ENCODINGS = [
    (RecurringTaskSkipRule.do_even(), "even"),
    (RecurringTaskSkipRule.do_odd(), "odd"),
    (RecurringTaskSkipRule.do_every_n_k(3, 0), "every 3 0"),
    (RecurringTaskSkipRule.do_every_n_k(5, 2), "every 5 2"),
    (
        RecurringTaskSkipRule.do_custom_daily_rel_weekly([1, 4]),
        "custom_daily_rel_weekly 1 4",
    ),
    (
        RecurringTaskSkipRule.do_custom_daily_rel_monthly([1, 15, 28]),
        "custom_daily_rel_monthly 1 15 28",
    ),
    (
        RecurringTaskSkipRule.do_custom_weekly_rel_yearly([1, 26, 52]),
        "custom_weekly_rel_yearly 1 26 52",
    ),
    (
        RecurringTaskSkipRule.do_custom_monthly_rel_yearly([1, 6, 12]),
        "custom_monthly_rel_yearly 1 6 12",
    ),
    (
        RecurringTaskSkipRule.do_custom_quarterly_rel_yearly([1, 2, 3]),
        "custom_quarterly_rel_yearly 1 2 3",
    ),
]


@pytest.mark.parametrize(("skip_rule", "encoding"), DATABASE_ENCODINGS)
def test_database_encoding(skip_rule: RecurringTaskSkipRule, encoding: str) -> None:
    encoder = RecurringTaskSkipRuleDatabaseEncoder()
    assert encoder.encode(skip_rule) == encoding


@pytest.mark.parametrize(("skip_rule", "encoding"), DATABASE_ENCODINGS)
def test_database_decoding(skip_rule: RecurringTaskSkipRule, encoding: str) -> None:
    decoder = RecurringTaskSkipRuleDatabaseDecoder()
    assert decoder.decode(encoding) == skip_rule


BAD_DATABASE_ENCODINGS = [
    "",
    "something_else",
    "even 3 2",
    "odd 1 2",
    "every",
    "every 3",
    "every 3 2 1",
    "every foo 3",
    "every 3 foo",
    "custom_daily_rel_weekly",
    "custom_daily_rel_weekly bar",
    "custom_daily_rel_weekly 1 bar",
    "custom_daily_rel_monthly",
    "custom_daily_rel_monthly bar",
    "custom_daily_rel_monthly 1 bar",
    "custom_weekly_rel_yearly",
    "custom_weekly_rel_yearly bar",
    "custom_weekly_rel_yearly 1 bar",
    "custom_monthly_rel_yearly",
    "custom_monthly_rel_yearly bar",
    "custom_monthly_rel_yearly 1 bar",
    "custom_quarterly_rel_yearly",
    "custom_quarterly_rel_yearly bar",
    "custom_quarterly_rel_yearly 1 bar",
]


@pytest.mark.parametrize("encoding", BAD_DATABASE_ENCODINGS)
def test_bad_database_decoding(encoding: str) -> None:
    decoder = RecurringTaskSkipRuleDatabaseDecoder()
    with pytest.raises(InputValidationError):
        decoder.decode(encoding)
