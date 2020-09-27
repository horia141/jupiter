"""Module for working with schedules."""
import abc
import typing
from typing import Optional

import pendulum
from pendulum import UTC
from pendulum.tz.timezone import Timezone

from models.basic import RecurringTaskPeriod, ADate, Timestamp


class Schedule(abc.ABC):
    """The base class for the schedule descriptors class."""

    _should_skip: bool
    _due_date: pendulum.Date
    _due_time: Optional[pendulum.DateTime]
    _full_name: str
    _timeline: str

    @staticmethod
    def year_two_digits(date: ADate) -> str:
        """Get the last two digits (decade and year) from a date."""
        return str(date.year % 100)

    @staticmethod
    def month_to_quarter_num(date: ADate) -> int:
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
            12: 4
        }

        return month_to_quarter_num[date.month]

    @staticmethod
    def month_to_quarter(date: ADate) -> str:
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
            12: "Q4"
        }

        return month_to_quarter[date.month]

    @staticmethod
    def month_to_quarter_start(date: ADate) -> int:
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
            12: 10
        }

        return month_to_quarter[date.month]

    @staticmethod
    def month_to_quarter_end(date: ADate) -> int:
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
            12: 12
        }

        return month_to_quarter[date.month]

    @staticmethod
    def month_to_month(date: ADate) -> str:
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
            12: "Dec"
        }

        return month_to_month[date.month]

    @property
    def should_skip(self) -> bool:
        """Whether the date should be skipped according to the planning rules."""
        return self._should_skip

    @property
    def due_time(self) -> ADate:
        """The due time of an event according to the schedule."""
        if self._due_time:
            return self._due_time
        else:
            return self._due_date

    @property
    def full_name(self) -> str:
        """The full name of the event with the schedule info in it."""
        return self._full_name

    @property
    def timeline(self) -> str:
        """The timeline of an event."""
        return self._timeline

    @staticmethod
    def _skip_helper(skip_rule: str, param: int) -> bool:
        if skip_rule == "even":
            return param % 2 == 0
        elif skip_rule == "odd":
            return param % 2 != 0
        else:
            # Why don't you write better programs, bro?
            return skip_rule.find(str(param)) != -1

    @property
    @abc.abstractmethod
    def period(self) -> RecurringTaskPeriod:
        """The period for the schedule."""

    @property
    @abc.abstractmethod
    def first_day(self) -> pendulum.Date:
        """The first day of the interval represented by the schedule block."""

    @property
    @abc.abstractmethod
    def end_day(self) -> pendulum.Date:
        """The end day of the interval represented by the schedule block."""

    def contains(self, timestamp: Timestamp) -> bool:
        """Tests whether a particular datetime is in the schedule block."""
        first_day_dt = pendulum.DateTime(self.first_day.year, self.first_day.month, self.first_day.day, tzinfo=UTC)
        end_day_dt = \
            pendulum.DateTime(self.end_day.year, self.end_day.month, self.end_day.day, tzinfo=UTC).end_of("day")
        return typing.cast(bool, first_day_dt <= timestamp) and typing.cast(bool, timestamp <= end_day_dt)


class DailySchedule(Schedule):
    """A daily schedule."""

    def __init__(self, name: str, right_now: Timestamp, timezone: Timezone, skip_rule: Optional[str] = None,
                 due_at_time: Optional[str] = None) -> None:
        """Construct a schedule."""
        self._date = right_now.date()
        self._due_date = right_now.date()
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time),
                tz=timezone)
        else:
            self._due_time = None
        self._full_name = "{name} {year}:{month}{day}".format(
            name=name, year=self.year_two_digits(right_now), month=self.month_to_month(right_now), day=right_now.day)
        self._timeline = self._generate_timeline(right_now)
        self._should_skip = self._skip_helper(skip_rule, self._due_date.day_of_week) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.DAILY

    @property
    def first_day(self) -> pendulum.Date:
        """The first day of the interval represented by the schedule block."""
        return self._due_date

    @property
    def end_day(self) -> pendulum.Date:
        """The end day of the interval represented by the schedule block."""
        return self._due_date

    def _generate_timeline(self, right_now: Timestamp) -> str:
        year = "{year}".format(year=right_now.year)
        quarter = self.month_to_quarter(right_now)
        month = self.month_to_month(right_now)
        week = "W{week}".format(week=right_now.week_of_year)
        day = "D{day}".format(day=right_now.day_of_week)

        return "{year},{quarter},{month},{week},{day}".format(year=year, quarter=quarter, month=month, week=week,
                                                              day=day)


class WeeklySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
            self, name: str, right_now: Timestamp, timezone: Timezone, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_week = right_now.start_of("week")
        self._date = right_now.date()
        if due_at_day:
            self._due_date = start_of_week.add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = start_of_week.end_of("week").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time), tz=timezone)
        else:
            self._due_time = None
        self._full_name = "{name} {year}:W{week}".format(
            name=name, year=self.year_two_digits(right_now), week=start_of_week.week_of_year)
        self._timeline = self._generate_timeline(start_of_week)
        self._should_skip = self._skip_helper(skip_rule, self._due_date.week_of_year) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.WEEKLY

    @property
    def first_day(self) -> pendulum.Date:
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("week")

    @property
    def end_day(self) -> pendulum.Date:
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("week")

    def _generate_timeline(self, right_now: Timestamp) -> str:
        year = "{year}".format(year=right_now.year)
        quarter = self.month_to_quarter(right_now)
        month = self.month_to_month(right_now)
        week = "W{week}".format(week=right_now.week_of_year)

        return "{year},{quarter},{month},{week}".format(year=year, quarter=quarter, month=month, week=week)


class MonthlySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
            self, name: str, right_now: Timestamp, timezone: Timezone, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_month = right_now.start_of("month")
        self._date = right_now.date()
        if due_at_day:
            self._due_date = start_of_month.add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = start_of_month.end_of("month").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time), tz=timezone)
        else:
            self._due_time = None
        self._full_name = "{name} {year}:{month}".format(
            name=name, year=self.year_two_digits(right_now), month=self.month_to_month(right_now))
        self._timeline = self._generate_timeline(Timestamp(start_of_month))
        self._should_skip = self._skip_helper(skip_rule, self._due_date.month) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.MONTHLY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("month")

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("month")

    def _generate_timeline(self, right_now: Timestamp) -> str:
        year = "{year}".format(year=right_now.year)
        quarter = self.month_to_quarter(right_now)
        month = self.month_to_month(right_now)

        return "{year},{quarter},{month}".format(year=year, quarter=quarter, month=month)


class QuarterlySchedule(Schedule):
    """A quarterly schedule."""

    def __init__(
            self, name: str, right_now: Timestamp, timezone: Timezone, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None,
            due_at_month: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = right_now.date()
        if due_at_month:
            if due_at_day:
                self._due_date = right_now\
                    .on(right_now.year, self.month_to_quarter_start(right_now), 1)\
                    .start_of("month")\
                    .add(months=due_at_month - 1)\
                    .add(days=due_at_day - 1)\
                    .end_of("day")
            else:
                self._due_date = right_now\
                    .on(right_now.year, self.month_to_quarter_start(right_now), 1)\
                    .start_of("month")\
                    .add(months=due_at_month - 1)\
                    .end_of("month")\
                    .end_of("day")
        elif due_at_day:
            self._due_date = right_now\
                .on(right_now.year, self.month_to_quarter_start(right_now), 1)\
                .start_of("month")\
                .add(days=due_at_day - 1)\
                .end_of("day")
        else:
            self._due_date = right_now\
                .on(right_now.year, self.month_to_quarter_end(right_now), 1)\
                .end_of("month")\
                .end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time), tz=timezone)
        else:
            self._due_time = None
        self._full_name = "{name} {year}:{quarter}".format(
            name=name, year=self.year_two_digits(right_now), quarter=self.month_to_quarter(right_now))
        self._timeline = self._generate_timeline(right_now)
        self._should_skip = \
            self._skip_helper(skip_rule, self.month_to_quarter_num(self._due_date)) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.QUARTERLY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return pendulum\
            .DateTime(self._date.year, self.month_to_quarter_start(self._date), self._date.day, tzinfo=UTC)\
            .start_of("month")

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the scedule block."""
        return pendulum\
            .DateTime(self._date.year, self.month_to_quarter_end(self._date), self._date.day, tzinfo=UTC)\
            .end_of("month")

    def _generate_timeline(self, right_now: Timestamp) -> str:
        year = "{year}".format(year=right_now.year)
        quarter = self.month_to_quarter(right_now)

        return "{year},{quarter}".format(year=year, quarter=quarter)


class YearlySchedule(Schedule):
    """A yearly schedule."""

    def __init__(
            self, name: str, right_now: Timestamp, timezone: Timezone, due_at_time: Optional[str] = None,
            due_at_day: Optional[int] = None, due_at_month: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = right_now.date()
        if due_at_month:
            if due_at_day:
                self._due_date = right_now\
                    .start_of("year")\
                    .add(months=due_at_month - 1)\
                    .add(days=due_at_day - 1)\
                    .end_of("day")
            else:
                self._due_date = right_now\
                    .start_of("year")\
                    .add(months=due_at_month - 1)\
                    .end_of("month")\
                    .end_of("day")
        elif due_at_day:
            self._due_date = right_now.start_of("year").add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = right_now.end_of("year").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time), tz=timezone)
        else:
            self._due_time = None
        self._full_name = "{name} {year}".format(name=name, year=self.year_two_digits(right_now))
        self._timeline = self._generate_timeline(right_now)
        self._should_skip = False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.YEARLY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("year")

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("year")

    @staticmethod
    def _generate_timeline(right_now: Timestamp) -> str:
        year = "{year}".format(year=right_now.year)

        return year


def get_schedule(
        period: RecurringTaskPeriod, name: str, right_now: Timestamp, timezone: Timezone,
        skip_rule: Optional[str] = None, due_at_time: Optional[str] = None, due_at_day: Optional[int] = None,
        due_at_month: Optional[int] = None) -> Schedule:
    """Build an appropriate schedule from the given parameters."""
    if period == RecurringTaskPeriod.DAILY:
        return DailySchedule(name, right_now, timezone, skip_rule, due_at_time)
    elif period == RecurringTaskPeriod.WEEKLY:
        return WeeklySchedule(name, right_now, timezone, skip_rule, due_at_time, due_at_day)
    elif period == RecurringTaskPeriod.MONTHLY:
        return MonthlySchedule(name, right_now, timezone, skip_rule, due_at_time, due_at_day)
    elif period == RecurringTaskPeriod.QUARTERLY:
        return QuarterlySchedule(name, right_now, timezone, skip_rule, due_at_time, due_at_day, due_at_month)
    elif period == RecurringTaskPeriod.YEARLY:
        return YearlySchedule(name, right_now, timezone, due_at_time, due_at_day, due_at_month)
    else:
        raise Exception(f"Invalid period {period}")
