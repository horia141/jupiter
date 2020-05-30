"""Module for working with schedules."""
import abc
from typing import Optional

import pendulum

from models.basic import RecurringTaskPeriod


class Schedule(abc.ABC):
    """The base class for the schedule descriptors class."""

    _should_skip: bool
    _due_date: pendulum.DateTime
    _due_time: Optional[pendulum.DateTime]
    _full_name: str
    _timeline: str

    @staticmethod
    def month_to_quarter_num(date: pendulum.DateTime) -> int:
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
    def month_to_quarter(date: pendulum.DateTime) -> str:
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
    def month_to_quarter_start(date: pendulum.DateTime) -> int:
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
    def month_to_quarter_end(date: pendulum.DateTime) -> int:
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
    def month_to_month(date: pendulum.DateTime) -> str:
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
    def due_time(self) -> pendulum.DateTime:
        """The due time of an event according to the schedule."""
        if self._due_time:
            return pendulum.DateTime(year=self._due_time.year,
                                     month=self._due_time.month,
                                     day=self._due_time.day,
                                     hour=self._due_time.hour,
                                     minute=self._due_time.minute,
                                     second=self._due_time.second)
        else:
            return pendulum.DateTime(year=self._due_date.year,
                                     month=self._due_date.month,
                                     day=self._due_date.day,
                                     hour=23,
                                     minute=59,
                                     second=59)

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
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""

    @property
    @abc.abstractmethod
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the schedule block."""
        return self._due_date


class DailySchedule(Schedule):
    """A daily schedule."""

    def __init__(self, name: str, date: pendulum.DateTime, skip_rule: Optional[str] = None,
                 due_at_time: Optional[str] = None) -> None:
        """Construct a schedule."""
        self._date = date
        self._due_date = date.end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time))
        else:
            self._due_time = None
        self._full_name = "{name} {month}{day}".format(name=name, month=self.month_to_month(date), day=date.day)
        self._timeline = self._generate_timeline(date)
        self._should_skip = self._skip_helper(skip_rule, self._due_date.day_of_week) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.DAILY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return self._due_date

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the schedule block."""
        return self._due_date

    def _generate_timeline(self, date: pendulum.DateTime) -> str:
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)
        week = "W{week}".format(week=date.week_of_year)
        day = "D{day}".format(day=date.day_of_week)

        return "{year},{quarter},{month},{week},{day}".format(year=year, quarter=quarter, month=month, week=week,
                                                              day=day)


class WeeklySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
            self, name: str, date: pendulum.DateTime, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_week = date.start_of("week")
        self._date = date
        if due_at_day:
            self._due_date = start_of_week.add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = start_of_week.end_of("week").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time))
        else:
            self._due_time = None
        self._full_name = "{name} W{week}".format(name=name, week=start_of_week.week_of_year)
        self._timeline = self._generate_timeline(start_of_week)
        self._should_skip = self._skip_helper(skip_rule, self._due_date.week_of_year) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.WEEKLY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("week")

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("week")

    def _generate_timeline(self, date: pendulum.DateTime) -> str:
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)
        week = "W{week}".format(week=date.week_of_year)

        return "{year},{quarter},{month},{week}".format(year=year, quarter=quarter, month=month, week=week)


class MonthlySchedule(Schedule):
    """A monthly schedule."""

    def __init__(
            self, name: str, date: pendulum.DateTime, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        start_of_month = date.start_of("month")
        self._date = date
        if due_at_day:
            self._due_date = start_of_month.add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = start_of_month.end_of("month").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time))
        else:
            self._due_time = None
        self._full_name = "{name} {month}".format(name=name, month=self.month_to_month(date))
        self._timeline = self._generate_timeline(start_of_month)
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

    def _generate_timeline(self, date: pendulum.DateTime) -> str:
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)

        return "{year},{quarter},{month}".format(year=year, quarter=quarter, month=month)


class QuarterlySchedule(Schedule):
    """A quarterly schedule."""

    def __init__(
            self, name: str, date: pendulum.DateTime, skip_rule: Optional[str] = None,
            due_at_time: Optional[str] = None, due_at_day: Optional[int] = None,
            due_at_month: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = date
        if due_at_month:
            if due_at_day:
                self._due_date = date.on(date.year, self.month_to_quarter_start(date), date.day).start_of("month").add(
                    months=due_at_month - 1).add(days=due_at_day - 1).end_of("day")
            else:
                self._due_date = date.on(date.year, self.month_to_quarter_start(date), date.day).start_of("month").add(
                    months=due_at_month - 1).end_of("month").end_of("day")
        elif due_at_day:
            self._due_date = date.on(date.year, self.month_to_quarter_start(date), date.day).start_of("month").add(
                days=due_at_day - 1).end_of("day")
        else:
            self._due_date = date.on(date.year, self.month_to_quarter_end(date), date.day).end_of("month").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time))
        else:
            self._due_time = None
        self._full_name = "{name} {quarter}".format(name=name, quarter=self.month_to_quarter(date))
        self._timeline = self._generate_timeline(date)
        self._should_skip = \
            self._skip_helper(skip_rule, self.month_to_quarter_num(self._due_date)) if skip_rule else False

    @property
    def period(self) -> RecurringTaskPeriod:
        """The period string."""
        return RecurringTaskPeriod.QUARTERLY

    @property
    def first_day(self) -> pendulum.DateTime:
        """The first day of the interval represented by the schedule block."""
        return self._date.on(self._date.year, self.month_to_quarter_end(self._date), self._date.day).start_of("month")

    @property
    def end_day(self) -> pendulum.DateTime:
        """The end day of the interval represented by the scedule block."""
        return self._date.on(self._date.year, self.month_to_quarter_end(self._date), self._date.day).end_of("month")

    def _generate_timeline(self, date: pendulum.DateTime) -> str:
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)

        return "{year},{quarter}".format(year=year, quarter=quarter)


class YearlySchedule(Schedule):
    """A yearly schedule."""

    def __init__(
            self, name: str, date: pendulum.DateTime, due_at_time: Optional[str] = None,
            due_at_day: Optional[int] = None, due_at_month: Optional[int] = None) -> None:
        """Construct a schedule."""
        super().__init__()
        self._date = date
        if due_at_month:
            if due_at_day:
                self._due_date = date.start_of("year").add(months=due_at_month - 1).add(days=due_at_day - 1).end_of(
                    "day")
            else:
                self._due_date = date.start_of("year").add(months=due_at_month - 1).end_of("month").end_of("day")
        elif due_at_day:
            self._due_date = date.start_of("year").add(days=due_at_day - 1).end_of("day")
        else:
            self._due_date = date.end_of("year").end_of("day")
        if due_at_time:
            self._due_time = pendulum.parse(
                "{date} {time}".format(date=self._due_date.to_date_string(), time=due_at_time))
        else:
            self._due_time = None
        self._full_name = "{name} {year}".format(name=name, year=date.year)
        self._timeline = self._generate_timeline(date)
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
    def _generate_timeline(date: pendulum.DateTime) -> str:
        year = "{year}".format(year=date.year)

        return year


def get_schedule(
        period: RecurringTaskPeriod, name: str, date: pendulum.DateTime, skip_rule: Optional[str] = None,
        due_at_time: Optional[str] = None, due_at_day: Optional[int] = None,
        due_at_month: Optional[int] = None) -> Schedule:
    """Build an appropriate schedule from the given parameters."""
    if period == RecurringTaskPeriod.DAILY:
        return DailySchedule(name, date, skip_rule, due_at_time)
    elif period == RecurringTaskPeriod.WEEKLY:
        return WeeklySchedule(name, date, skip_rule, due_at_time, due_at_day)
    elif period == RecurringTaskPeriod.MONTHLY:
        return MonthlySchedule(name, date, skip_rule, due_at_time, due_at_day)
    elif period == RecurringTaskPeriod.QUARTERLY:
        return QuarterlySchedule(name, date, skip_rule, due_at_time, due_at_day, due_at_month)
    elif period == RecurringTaskPeriod.YEARLY:
        return YearlySchedule(name, date, due_at_time, due_at_day, due_at_month)
    else:
        raise Exception(f"Invalid period {period}")