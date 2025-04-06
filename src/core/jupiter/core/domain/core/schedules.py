"""Module for working with schedules."""

import abc
from typing import cast

from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC


class Schedule(abc.ABC):
    """The base class for the schedule descriptors class."""

    _should_keep: bool
    _actionable_date: Date | None
    _date: Date
    _due_date: Date
    _full_name: InboxTaskName
    _timeline: str

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Schedule({self.period} {self.first_day} {self.end_day} {self.timeline})"
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Schedule({self.period} {self.first_day} {self.end_day} {self.timeline})"
        )

    @staticmethod
    def year_big(date: Timestamp) -> str:
        """Get the last two digits (decade and year) from a date."""
        return date.value.format("YYYY")

    @staticmethod
    def month_to_quarter_num(date: Date) -> int:
        """Map a date to one of the four quarters from the year."""
        month_to_quarter_num = {
            1: 1,
            2: 1,
            3: 1,
            4: 2,
            5: 2,
            6: 2,
            7: 3,
            8: 3,
            9: 3,
            10: 4,
            11: 4,
            12: 4,
        }

        return month_to_quarter_num[date.month]

    @staticmethod
    def month_to_quarter(date: Timestamp) -> str:
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

    @staticmethod
    def month_to_quarter_start(date: Timestamp | Date) -> int:
        """Map a month in a date to the first month of a quarter of which the date belongs."""
        month_to_quarter = {
            1: 1,
            2: 1,
            3: 1,
            4: 4,
            5: 4,
            6: 4,
            7: 7,
            8: 7,
            9: 7,
            10: 10,
            11: 10,
            12: 10,
        }

        return month_to_quarter[date.month]

    @staticmethod
    def month_to_quarter_end(date: Timestamp | Date) -> int:
        """Map a month in a date to the last month of a quarter of which the date belongs."""
        month_to_quarter = {
            1: 3,
            2: 3,
            3: 3,
            4: 6,
            5: 6,
            6: 6,
            7: 9,
            8: 9,
            9: 9,
            10: 12,
            11: 12,
            12: 12,
        }

        return month_to_quarter[date.month]

    @staticmethod
    def month_to_month(date: Timestamp) -> str:
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

    @property
    def should_keep(self) -> bool:
        """Whether the date should be skipped according to the planning rules."""
        return self._should_keep

    @property
    def actionable_date(self) -> ADate | None:
        """The actionable date for the schedule, if any."""
        return ADate.from_date(self._actionable_date) if self._actionable_date else None

    @property
    def due_date(self) -> ADate:
        """The due date of the schedule."""
        return ADate.from_date(self._due_date)

    @property
    def full_name(self) -> InboxTaskName:
        """The full name of the event with the schedule info in it."""
        return self._full_name

    @property
    def timeline(self) -> str:
        """The timeline of an event."""
        return self._timeline

    @property
    @abc.abstractmethod
    def period(self) -> RecurringTaskPeriod:
        """The period for the schedule."""

    @property
    @abc.abstractmethod
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""

    @property
    @abc.abstractmethod
    def end_day(self) -> ADate:
        """The end day of the interval represented by the schedule block."""

    def contains_timestamp(self, timestamp: Timestamp) -> bool:
        """Tests whether a particular datetime is in the schedule block."""
        first_day_dt = DateTime(
            self.first_day.year,
            self.first_day.month,
            self.first_day.day,
            tzinfo=UTC,
        )
        end_day_dt = DateTime(
            self.end_day.year,
            self.end_day.month,
            self.end_day.day,
            tzinfo=UTC,
        ).end_of("day")
        ts = timestamp.value.end_of("day")
        return first_day_dt <= ts and ts <= end_day_dt


class DailySchedule(Schedule):
    """A daily schedule."""

    def __init__(
        self,
        name: EntityName,
        right_now: Timestamp,
        skip_rule: RecurringTaskSkipRule | None = None,
    ) -> None:
        """Construct a schedule."""
        self._date = cast(Date, right_now.value.date())
        self._due_date = cast(Date, right_now.value.date())
        self._actionable_date = None
        self._full_name = InboxTaskName(
            f"{name} {self.year_big(right_now)}:{self.month_to_month(right_now)}{right_now.value.day}",
        )
        self._timeline = infer_timeline(RecurringTaskPeriod.DAILY, right_now)
        self._should_keep = (
            skip_rule.should_keep(RecurringTaskPeriod.DAILY, self._due_date)
            if skip_rule
            else True
        )

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.DAILY

    @property
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""
        return ADate.from_date(self._due_date)

    @property
    def end_day(self) -> ADate:
        """The end day of the interval represented by the schedule block."""
        return ADate.from_date(self._due_date)


class WeeklySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
        self,
        name: EntityName,
        right_now: Timestamp,
        skip_rule: RecurringTaskSkipRule | None,
        actionable_from_day: RecurringTaskDueAtDay | None,
        due_at_day: RecurringTaskDueAtDay | None,
    ) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_week = right_now.value.start_of("week")
        self._date = cast(Date, right_now.value.date())
        if actionable_from_day:
            self._actionable_date = cast(
                Date,
                start_of_week.add(days=actionable_from_day.as_int() - 1).date(),
            )
        else:
            self._actionable_date = None
        if due_at_day:
            self._due_date = start_of_week.add(days=due_at_day.as_int() - 1).end_of(
                "day",
            )
        else:
            self._due_date = start_of_week.end_of("week").end_of("day")
        self._full_name = InboxTaskName(
            f"{name} {self.year_big(right_now)}:W{start_of_week.week_of_year}",
        )
        self._timeline = infer_timeline(RecurringTaskPeriod.WEEKLY, right_now)
        self._should_keep = (
            skip_rule.should_keep(RecurringTaskPeriod.WEEKLY, self._due_date)
            if skip_rule
            else True
        )

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.WEEKLY

    @property
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.start_of("week"))

    @property
    def end_day(self) -> ADate:
        """The end day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.end_of("week"))


class MonthlySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
        self,
        name: EntityName,
        right_now: Timestamp,
        skip_rule: RecurringTaskSkipRule | None,
        actionable_from_day: RecurringTaskDueAtDay | None,
        due_at_day: RecurringTaskDueAtDay | None,
    ) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_month = right_now.value.start_of("month")
        self._date = cast(Date, right_now.value.date())
        if actionable_from_day:
            self._actionable_date = cast(
                Date,
                start_of_month.add(days=actionable_from_day.as_int() - 1).date(),
            )
        else:
            self._actionable_date = None
        if due_at_day:
            self._due_date = start_of_month.add(days=due_at_day.as_int() - 1).end_of(
                "day",
            )
        else:
            self._due_date = start_of_month.end_of("month").end_of("day")
        self._full_name = InboxTaskName(
            f"{name} {self.year_big(right_now)}:{self.month_to_month(right_now)}",
        )
        self._timeline = infer_timeline(RecurringTaskPeriod.MONTHLY, right_now)
        self._should_keep = (
            skip_rule.should_keep(RecurringTaskPeriod.MONTHLY, self._due_date)
            if skip_rule
            else True
        )

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.MONTHLY

    @property
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.start_of("month"))

    @property
    def end_day(self) -> ADate:
        """The end day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.end_of("month"))


class QuarterlySchedule(Schedule):
    """A quarterly schedule."""

    def __init__(
        self,
        name: EntityName,
        right_now: Timestamp,
        skip_rule: RecurringTaskSkipRule | None,
        actionable_from_day: RecurringTaskDueAtDay | None,
        actionable_from_month: RecurringTaskDueAtMonth | None,
        due_at_day: RecurringTaskDueAtDay | None,
        due_at_month: RecurringTaskDueAtMonth | None,
    ) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = cast(Date, right_now.value.date())
        if actionable_from_month:
            if actionable_from_day:
                self._actionable_date = cast(
                    Date,
                    right_now.value.on(
                        right_now.value.year,
                        self.month_to_quarter_start(right_now),
                        1,
                    )
                    .start_of("month")
                    .add(months=actionable_from_month.as_int() - 1)
                    .add(days=actionable_from_day.as_int() - 1)
                    .date(),
                )
            else:
                self._actionable_date = cast(
                    Date,
                    right_now.value.on(
                        right_now.value.year,
                        self.month_to_quarter_start(right_now),
                        1,
                    )
                    .start_of("month")
                    .add(months=actionable_from_month.as_int() - 1)
                    .date(),
                )
        elif actionable_from_day:
            self._actionable_date = cast(
                Date,
                right_now.value.on(
                    right_now.value.year,
                    self.month_to_quarter_start(right_now),
                    1,
                )
                .start_of("month")
                .add(days=actionable_from_day.as_int() - 1)
                .date(),
            )
        else:
            self._actionable_date = None
        if due_at_month:
            if due_at_day:
                self._due_date = (
                    right_now.value.on(
                        right_now.value.year,
                        self.month_to_quarter_start(right_now),
                        1,
                    )
                    .start_of("month")
                    .add(months=due_at_month.as_int() - 1)
                    .add(days=due_at_day.as_int() - 1)
                    .end_of("day")
                )
            else:
                self._due_date = (
                    right_now.value.on(
                        right_now.value.year,
                        self.month_to_quarter_start(right_now),
                        1,
                    )
                    .start_of("month")
                    .add(months=due_at_month.as_int() - 1)
                    .end_of("month")
                    .end_of("day")
                )
        elif due_at_day:
            self._due_date = (
                right_now.value.on(
                    right_now.value.year,
                    self.month_to_quarter_start(right_now),
                    1,
                )
                .start_of("month")
                .add(days=due_at_day.as_int() - 1)
                .end_of("day")
            )
        else:
            self._due_date = (
                right_now.value.on(
                    right_now.value.year,
                    self.month_to_quarter_end(right_now),
                    1,
                )
                .end_of("month")
                .end_of("day")
            )
        self._full_name = InboxTaskName(
            f"{name} {self.year_big(right_now)}:{self.month_to_quarter(right_now)}",
        )
        self._timeline = infer_timeline(RecurringTaskPeriod.QUARTERLY, right_now)
        self._should_keep = (
            skip_rule.should_keep(RecurringTaskPeriod.QUARTERLY, self._due_date)
            if skip_rule
            else True
        )

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.QUARTERLY

    @property
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""
        return ADate.from_date(
            Date(
                self._date.year,
                self.month_to_quarter_start(self._date),
                self._date.day,
            ).start_of("month"),
        )

    @property
    def end_day(self) -> ADate:
        """The end day of the interval represented by the scedule block."""
        return ADate.from_date(
            Date(
                self._date.year,
                self.month_to_quarter_end(self._date),
                self._date.day,
            ).end_of("month"),
        )


class YearlySchedule(Schedule):
    """A yearly schedule."""

    def __init__(
        self,
        name: EntityName,
        right_now: Timestamp,
        skip_rule: RecurringTaskSkipRule | None,
        actionable_from_day: RecurringTaskDueAtDay | None,
        actionable_from_month: RecurringTaskDueAtMonth | None,
        due_at_day: RecurringTaskDueAtDay | None,
        due_at_month: RecurringTaskDueAtMonth | None,
    ) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = cast(Date, right_now.value.date())
        if actionable_from_month:
            if actionable_from_day:
                self._actionable_date = cast(
                    Date,
                    right_now.value.start_of("year")
                    .add(months=actionable_from_month.as_int() - 1)
                    .add(days=actionable_from_day.as_int() - 1)
                    .date(),
                )
            else:
                self._actionable_date = cast(
                    Date,
                    right_now.value.start_of("year")
                    .add(months=actionable_from_month.as_int() - 1)
                    .date(),
                )
        elif actionable_from_day:
            self._actionable_date = cast(
                Date,
                right_now.value.start_of("year")
                .add(days=actionable_from_day.as_int() - 1)
                .date(),
            )
        else:
            self._actionable_date = None
        if due_at_month:
            if due_at_day:
                self._due_date = (
                    right_now.value.start_of("year")
                    .add(months=due_at_month.as_int() - 1)
                    .add(days=due_at_day.as_int() - 1)
                    .end_of("day")
                )
            else:
                self._due_date = (
                    right_now.value.start_of("year")
                    .add(months=due_at_month.as_int() - 1)
                    .end_of("month")
                    .end_of("day")
                )
        elif due_at_day:
            self._due_date = (
                right_now.value.start_of("year")
                .add(days=due_at_day.as_int() - 1)
                .end_of("day")
            )
        else:
            self._due_date = right_now.value.end_of("year").end_of("day")
        self._full_name = InboxTaskName(f"{name} {self.year_big(right_now)}")
        self._timeline = infer_timeline(RecurringTaskPeriod.YEARLY, right_now)
        self._should_keep = (
            skip_rule.should_keep(RecurringTaskPeriod.YEARLY, self._due_date)
            if skip_rule
            else True
        )

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.YEARLY

    @property
    def first_day(self) -> ADate:
        """The first day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.start_of("year"))

    @property
    def end_day(self) -> ADate:
        """The end day of the interval represented by the schedule block."""
        return ADate.from_date(self._date.end_of("year"))


def get_schedule(
    period: RecurringTaskPeriod,
    name: EntityName,
    right_now: Timestamp,
    skip_rule: RecurringTaskSkipRule | None = None,
    actionable_from_day: RecurringTaskDueAtDay | None = None,
    actionable_from_month: RecurringTaskDueAtMonth | None = None,
    due_at_day: RecurringTaskDueAtDay | None = None,
    due_at_month: RecurringTaskDueAtMonth | None = None,
) -> Schedule:
    """Build an appropriate schedule from the given parameters."""
    if period == RecurringTaskPeriod.DAILY:
        return DailySchedule(name, right_now, skip_rule)
    elif period == RecurringTaskPeriod.WEEKLY:
        return WeeklySchedule(
            name,
            right_now,
            skip_rule,
            actionable_from_day,
            due_at_day,
        )
    elif period == RecurringTaskPeriod.MONTHLY:
        return MonthlySchedule(
            name,
            right_now,
            skip_rule,
            actionable_from_day,
            due_at_day,
        )
    elif period == RecurringTaskPeriod.QUARTERLY:
        return QuarterlySchedule(
            name,
            right_now,
            skip_rule,
            actionable_from_day,
            actionable_from_month,
            due_at_day,
            due_at_month,
        )
    elif period == RecurringTaskPeriod.YEARLY:
        return YearlySchedule(
            name,
            right_now,
            skip_rule,
            actionable_from_day,
            actionable_from_month,
            due_at_day,
            due_at_month,
        )
    else:
        raise Exception(f"Invalid period {period}")
