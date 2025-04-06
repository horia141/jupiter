"""Tests for the habit repeats strategy."""

import pytest
from jupiter.core.domain.concept.habits.habit_repeats_strategy import (
    HabitRepeatsStrategy,
)
from jupiter.core.domain.core.adate import ADate

START_DATE = ADate.from_str("2024-01-01")
END_DATE = ADate.from_str("2024-01-07")
END_DATE_MONTH = ADate.from_str("2024-01-31")
END_DATE_QUARTER = ADate.from_str("2024-03-31")
END_DATE_YEAR = ADate.from_str("2024-12-31")
ALL_SAME_TEST_CASES = [
    (
        3,
        [
            (START_DATE, END_DATE),
            (START_DATE, END_DATE),
            (START_DATE, END_DATE),
        ],
    ),
    (
        2,
        [
            (START_DATE, END_DATE),
            (START_DATE, END_DATE),
        ],
    ),
]


@pytest.mark.parametrize(
    ("repeats_in_period", "expected"),
    ALL_SAME_TEST_CASES,
)
def test_spread_tasks_all_same(
    repeats_in_period: int, expected: list[tuple[ADate, ADate]]
) -> None:
    """Test the spread tasks method with the all same strategy."""
    assert (
        HabitRepeatsStrategy.ALL_SAME.spread_tasks(
            START_DATE, END_DATE, repeats_in_period
        )
        == expected
    )


SPREAD_OUT_NO_OVERLAP_TEST_CASES_WEEKLY = [
    (
        2,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-07")),
        ],
    ),
    (
        3,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-03")),
            (ADate.from_str("2024-01-04"), ADate.from_str("2024-01-05")),
            (ADate.from_str("2024-01-06"), ADate.from_str("2024-01-07")),
        ],
    ),
    (
        4,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-02")),
            (ADate.from_str("2024-01-03"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-06")),
            (ADate.from_str("2024-01-07"), ADate.from_str("2024-01-07")),
        ],
    ),
    (
        5,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-02")),
            (ADate.from_str("2024-01-03"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-05")),
            (ADate.from_str("2024-01-06"), ADate.from_str("2024-01-06")),
            (ADate.from_str("2024-01-07"), ADate.from_str("2024-01-07")),
        ],
    ),
    (
        6,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-02")),
            (ADate.from_str("2024-01-03"), ADate.from_str("2024-01-03")),
            (ADate.from_str("2024-01-04"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-05")),
            (ADate.from_str("2024-01-06"), ADate.from_str("2024-01-06")),
            (ADate.from_str("2024-01-07"), ADate.from_str("2024-01-07")),
        ],
    ),
    (
        7,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-01")),
            (ADate.from_str("2024-01-02"), ADate.from_str("2024-01-02")),
            (ADate.from_str("2024-01-03"), ADate.from_str("2024-01-03")),
            (ADate.from_str("2024-01-04"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-05")),
            (ADate.from_str("2024-01-06"), ADate.from_str("2024-01-06")),
            (ADate.from_str("2024-01-07"), ADate.from_str("2024-01-07")),
        ],
    ),
]


@pytest.mark.parametrize(
    ("repeats_in_period", "expected"),
    SPREAD_OUT_NO_OVERLAP_TEST_CASES_WEEKLY,
)
def test_spread_tasks_spread_out_no_overlap_weekly(
    repeats_in_period: int, expected: list[tuple[ADate, ADate]]
) -> None:
    """Test the spread tasks method with the spread out no overlap strategy."""
    assert (
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(
            START_DATE, END_DATE, repeats_in_period
        )
        == expected
    )


SPREAD_OUT_NO_OVERLAP_TEST_CASES_MONTHLY = [
    (
        2,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-16")),
            (ADate.from_str("2024-01-17"), ADate.from_str("2024-01-31")),
        ],
    ),
    (
        3,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-11")),
            (ADate.from_str("2024-01-12"), ADate.from_str("2024-01-21")),
            (ADate.from_str("2024-01-22"), ADate.from_str("2024-01-31")),
        ],
    ),
    (
        4,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-08")),
            (ADate.from_str("2024-01-09"), ADate.from_str("2024-01-16")),
            (ADate.from_str("2024-01-17"), ADate.from_str("2024-01-24")),
            (ADate.from_str("2024-01-25"), ADate.from_str("2024-01-31")),
        ],
    ),
    (
        5,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-07")),
            (ADate.from_str("2024-01-08"), ADate.from_str("2024-01-13")),
            (ADate.from_str("2024-01-14"), ADate.from_str("2024-01-19")),
            (ADate.from_str("2024-01-20"), ADate.from_str("2024-01-25")),
            (ADate.from_str("2024-01-26"), ADate.from_str("2024-01-31")),
        ],
    ),
    (
        10,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-07")),
            (ADate.from_str("2024-01-08"), ADate.from_str("2024-01-10")),
            (ADate.from_str("2024-01-11"), ADate.from_str("2024-01-13")),
            (ADate.from_str("2024-01-14"), ADate.from_str("2024-01-16")),
            (ADate.from_str("2024-01-17"), ADate.from_str("2024-01-19")),
            (ADate.from_str("2024-01-20"), ADate.from_str("2024-01-22")),
            (ADate.from_str("2024-01-23"), ADate.from_str("2024-01-25")),
            (ADate.from_str("2024-01-26"), ADate.from_str("2024-01-28")),
            (ADate.from_str("2024-01-29"), ADate.from_str("2024-01-31")),
        ],
    ),
    (
        31,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-01")),
            (ADate.from_str("2024-01-02"), ADate.from_str("2024-01-02")),
            (ADate.from_str("2024-01-03"), ADate.from_str("2024-01-03")),
            (ADate.from_str("2024-01-04"), ADate.from_str("2024-01-04")),
            (ADate.from_str("2024-01-05"), ADate.from_str("2024-01-05")),
            (ADate.from_str("2024-01-06"), ADate.from_str("2024-01-06")),
            (ADate.from_str("2024-01-07"), ADate.from_str("2024-01-07")),
            (ADate.from_str("2024-01-08"), ADate.from_str("2024-01-08")),
            (ADate.from_str("2024-01-09"), ADate.from_str("2024-01-09")),
            (ADate.from_str("2024-01-10"), ADate.from_str("2024-01-10")),
            (ADate.from_str("2024-01-11"), ADate.from_str("2024-01-11")),
            (ADate.from_str("2024-01-12"), ADate.from_str("2024-01-12")),
            (ADate.from_str("2024-01-13"), ADate.from_str("2024-01-13")),
            (ADate.from_str("2024-01-14"), ADate.from_str("2024-01-14")),
            (ADate.from_str("2024-01-15"), ADate.from_str("2024-01-15")),
            (ADate.from_str("2024-01-16"), ADate.from_str("2024-01-16")),
            (ADate.from_str("2024-01-17"), ADate.from_str("2024-01-17")),
            (ADate.from_str("2024-01-18"), ADate.from_str("2024-01-18")),
            (ADate.from_str("2024-01-19"), ADate.from_str("2024-01-19")),
            (ADate.from_str("2024-01-20"), ADate.from_str("2024-01-20")),
            (ADate.from_str("2024-01-21"), ADate.from_str("2024-01-21")),
            (ADate.from_str("2024-01-22"), ADate.from_str("2024-01-22")),
            (ADate.from_str("2024-01-23"), ADate.from_str("2024-01-23")),
            (ADate.from_str("2024-01-24"), ADate.from_str("2024-01-24")),
            (ADate.from_str("2024-01-25"), ADate.from_str("2024-01-25")),
            (ADate.from_str("2024-01-26"), ADate.from_str("2024-01-26")),
            (ADate.from_str("2024-01-27"), ADate.from_str("2024-01-27")),
            (ADate.from_str("2024-01-28"), ADate.from_str("2024-01-28")),
            (ADate.from_str("2024-01-29"), ADate.from_str("2024-01-29")),
            (ADate.from_str("2024-01-30"), ADate.from_str("2024-01-30")),
            (ADate.from_str("2024-01-31"), ADate.from_str("2024-01-31")),
        ],
    ),
]


@pytest.mark.parametrize(
    ("repeats_in_period", "expected"),
    SPREAD_OUT_NO_OVERLAP_TEST_CASES_MONTHLY,
)
def test_spread_tasks_spread_out_no_overlap_monthly(
    repeats_in_period: int, expected: list[tuple[ADate, ADate]]
) -> None:
    """Test the spread tasks method with the spread out no overlap strategy."""
    assert (
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(
            START_DATE, END_DATE_MONTH, repeats_in_period
        )
        == expected
    )


SPREAD_OUT_NO_OVERLAP_TEST_CASES_QUARTERLY = [
    (
        2,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-02-15")),
            (ADate.from_str("2024-02-16"), ADate.from_str("2024-03-31")),
        ],
    ),
    (
        3,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-01-31")),
            (ADate.from_str("2024-02-01"), ADate.from_str("2024-03-01")),
            (ADate.from_str("2024-03-02"), ADate.from_str("2024-03-31")),
        ],
    ),
]


@pytest.mark.parametrize(
    ("repeats_in_period", "expected"),
    SPREAD_OUT_NO_OVERLAP_TEST_CASES_QUARTERLY,
)
def test_spread_tasks_spread_out_no_overlap_quarterly(
    repeats_in_period: int, expected: list[tuple[ADate, ADate]]
) -> None:
    """Test the spread tasks method with the spread out no overlap strategy."""
    assert (
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(
            START_DATE, END_DATE_QUARTER, repeats_in_period
        )
        == expected
    )


SPREAD_OUT_NO_OVERLAP_TEST_CASES_YEARLY = [
    (
        2,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-07-01")),
            (ADate.from_str("2024-07-02"), ADate.from_str("2024-12-31")),
        ],
    ),
    (
        10,
        [
            (ADate.from_str("2024-01-01"), ADate.from_str("2024-02-06")),
            (ADate.from_str("2024-02-07"), ADate.from_str("2024-03-14")),
            (ADate.from_str("2024-03-15"), ADate.from_str("2024-04-20")),
            (ADate.from_str("2024-04-21"), ADate.from_str("2024-05-27")),
            (ADate.from_str("2024-05-28"), ADate.from_str("2024-07-03")),
            (ADate.from_str("2024-07-04"), ADate.from_str("2024-08-09")),
            (ADate.from_str("2024-08-10"), ADate.from_str("2024-09-14")),
            (ADate.from_str("2024-09-15"), ADate.from_str("2024-10-20")),
            (ADate.from_str("2024-10-21"), ADate.from_str("2024-11-25")),
            (ADate.from_str("2024-11-26"), ADate.from_str("2024-12-31")),
        ],
    ),
]


@pytest.mark.parametrize(
    ("repeats_in_period", "expected"),
    SPREAD_OUT_NO_OVERLAP_TEST_CASES_YEARLY,
)
def test_spread_tasks_spread_out_no_overlap_yearly(
    repeats_in_period: int, expected: list[tuple[ADate, ADate]]
) -> None:
    """Test the spread tasks method with the spread out no overlap strategy."""
    assert (
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(
            START_DATE, END_DATE_YEAR, repeats_in_period
        )
        == expected
    )


def test_spread_tasks_start_date_after_end_date() -> None:
    """Test the spread tasks method with the start date after the end date."""
    with pytest.raises(ValueError, match="The start date must be before the end date"):
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(END_DATE, START_DATE, 1)


def test_spread_tasks_repeats_in_period_less_than_1() -> None:
    """Test the spread tasks method with the repeats in period less than 1."""
    with pytest.raises(
        ValueError, match="The number of repeats in period must be at least 1"
    ):
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(START_DATE, END_DATE, 0)


def test_spread_tasks_duration_days_less_than_repeats_in_period() -> None:
    """Test the spread tasks method with the duration days less than the repeats in period."""
    with pytest.raises(
        ValueError,
        match="The number of days in the period is less than the repeat count",
    ):
        HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP.spread_tasks(
            START_DATE, END_DATE, 10
        )
