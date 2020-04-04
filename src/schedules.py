"""Module for working with schedules."""

import datetime

import pendulum

PERIODS = frozenset([
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "yearly"
])


class Schedule:
    """The base class for the schedule descriptors class."""

    def __init__(self):
        """Construct a schedule."""
        self._should_skip = None
        self._due_time = None
        self._due_date = None
        self._full_name = None
        self._timeline = None

    @staticmethod
    def month_to_quarter_num(date):
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
    def month_to_quarter(date):
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
    def month_to_quarter_start(date):
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
    def month_to_quarter_end(date):
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
    def month_to_month(date):
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
    def should_skip(self):
        """Whether the date should be skipped according to the planning rules."""
        return self._should_skip

    @property
    def due_time(self):
        """The due time of an event according to the schedule."""
        if self._due_time:
            return datetime.datetime(year=self._due_time.year,
                                     month=self._due_time.month,
                                     day=self._due_time.day,
                                     hour=self._due_time.hour,
                                     minute=self._due_time.minute,
                                     second=self._due_time.second)
        else:
            return datetime.date(year=self._due_date.year, month=self._due_date.month, day=self._due_date.day)

    @property
    def full_name(self):
        """The full name of the event with the schedule info in it."""
        return self._full_name

    @property
    def timeline(self):
        """The timeline of an event."""
        return self._timeline

    @staticmethod
    def _skip_helper(skip_rule: str, param):
        if skip_rule == "even":
            return param % 2 == 0
        elif skip_rule == "odd":
            return param % 2 != 0
        else:
            # Why don't you write better programs, bro?
            return skip_rule.find(str(param)) != -1


class DailySchedule(Schedule):
    """A daily schedule."""

    def __init__(self, name, date, skip_rule=None, due_at_time=None):
        """Construct a schedule."""
        super().__init__()
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
    def period(self):
        """The period string."""
        return "Daily"

    @property
    def first_day(self):
        """The first day of the interval represented by the schedule block."""
        return self._due_date

    @property
    def end_day(self):
        """The end day of the interval represented by the schedule block."""
        return self._due_date

    def _generate_timeline(self, date):
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)
        week = "W{week}".format(week=date.week_of_year)
        day = "D{day}".format(day=date.day_of_week)

        return "{year},{quarter},{month},{week},{day}".format(year=year, quarter=quarter, month=month, week=week,
                                                              day=day)


class WeeklySchedule(Schedule):
    """A monthly schedule."""

    def __init__(self, name, date, skip_rule=None, due_at_time=None, due_at_day=None):
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
    def period(self):
        """The period string."""
        return "Weekly"

    @property
    def first_day(self):
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("week")

    @property
    def end_day(self):
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("week")

    def _generate_timeline(self, date):
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)
        week = "W{week}".format(week=date.week_of_year)

        return "{year},{quarter},{month},{week}".format(year=year, quarter=quarter, month=month, week=week)


class MonthlySchedule(Schedule):
    """A monthly schedule."""

    def __init__(self, name, date, skip_rule=None, due_at_time=None, due_at_day=None):
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
    def period(self):
        """The period string."""
        return "Monthly"

    @property
    def first_day(self):
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("month")

    @property
    def end_day(self):
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("month")

    def _generate_timeline(self, date):
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)
        month = self.month_to_month(date)

        return "{year},{quarter},{month}".format(year=year, quarter=quarter, month=month)


class QuarterlySchedule(Schedule):
    """A quarterly schedule."""

    def __init__(self, name, date, skip_rule=None, due_at_time=None, due_at_day=None, due_at_month=None):
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
    def period(self):
        """The period string."""
        return "Quarterly"

    @property
    def first_day(self):
        """The first day of the interval represented by the schedule block."""
        return self._date.on(self._date.year, self.month_to_quarter_end(self._date), self._date.day).start_of("month")

    @property
    def end_day(self):
        """The end day of the interval represented by the scedule block."""
        return self._date.on(self._date.year, self.month_to_quarter_end(self._date), self._date.day).end_of("month")

    def _generate_timeline(self, date):
        year = "{year}".format(year=date.year)
        quarter = self.month_to_quarter(date)

        return "{year},{quarter}".format(year=year, quarter=quarter)


class YearlySchedule(Schedule):
    """A yearly schedule."""

    def __init__(self, name, date, due_at_time=None, due_at_day=None, due_at_month=None):
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
    def period(self):
        """The period string."""
        return "Yearly"

    @property
    def first_day(self):
        """The first day of the interval represented by the schedule block."""
        return self._date.start_of("year")

    @property
    def end_day(self):
        """The end day of the interval represented by the schedule block."""
        return self._date.end_of("year")

    @staticmethod
    def _generate_timeline(date):
        year = "{year}".format(year=date.year)

        return year


def get_schedule(period, name, date, skip_rule, due_at_time=None, due_at_day=None, due_at_month=None):
    """Build an appropriate schedule from the given parameters."""
    clean_period = period.lower()
    if clean_period == "daily":
        return DailySchedule(name, date, skip_rule, due_at_time)
    elif clean_period == "weekly":
        return WeeklySchedule(name, date, skip_rule, due_at_time, due_at_day)
    elif clean_period == "monthly":
        return MonthlySchedule(name, date, skip_rule, due_at_time, due_at_day)
    elif clean_period == "quarterly":
        return QuarterlySchedule(name, date, skip_rule, due_at_time, due_at_day, due_at_month)
    elif clean_period == "yearly":
        return YearlySchedule(name, date, due_at_time, due_at_day, due_at_month)
    else:
        raise Exception("Invalid period {period}".format(period=period))
