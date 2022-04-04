"""A date or possibly a datetime for the application."""
import datetime
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional, cast

from notion.collection import NotionDate
import pendulum
from pendulum.tz import UTC

from jupiter.domain.timezone import Timezone
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
@total_ordering
class ADate(Value):
    """A date or possibly a datetime for the application."""

    _the_date: Optional[pendulum.Date]
    _the_datetime: Optional[pendulum.DateTime]

    @staticmethod
    def from_date(date: pendulum.Date) -> 'ADate':
        """Construct an ADate from a date."""
        return ADate(date, None)

    @staticmethod
    def from_date_and_time(date_and_time: pendulum.DateTime) -> 'ADate':
        """Construct an ADate from a datetime."""
        return ADate(None, date_and_time)

    @staticmethod
    def from_timestamp(timestamp: Timestamp) -> 'ADate':
        """Construct an ADate from a timestamp."""
        return ADate(None, timestamp.value)

    @staticmethod
    def from_raw(timezone: Timezone, datetime_raw: Optional[str]) -> 'ADate':
        """Validate and clean an ADate."""
        if not datetime_raw:
            raise InputValidationError("Expected datetime to be non-null")

        try:
            adate = pendulum.parse(datetime_raw, tz=pendulum.timezone(str(timezone)), exact=True)

            if isinstance(adate, pendulum.DateTime):
                return ADate(None, adate.in_timezone(UTC))
            elif isinstance(adate, pendulum.Date):
                return ADate(adate, None)
            else:
                raise InputValidationError(f"Expected datetime '{datetime_raw}' to be in a proper datetime format")
        except pendulum.parsing.exceptions.ParserError as error:
            raise InputValidationError(f"Expected datetime '{datetime_raw}' to be in a proper format") from error

    @staticmethod
    def from_str(date_raw: str) -> 'ADate':
        """Parse a date from string."""
        return ADate(pendulum.parse(date_raw.replace(" 00:00:00", ""), tz=UTC, exact=True), None)

    @staticmethod
    def from_db(timestamp_raw: datetime.datetime) -> 'ADate':
        """Parse a timestamp from a DB representation."""
        return ADate(None, pendulum.instance(timestamp_raw).in_timezone(UTC))

    @staticmethod
    def from_notion(timezone: Timezone, adate_raw: NotionDate) -> 'ADate':
        """Parse a date from a Notion representation."""
        adate_raw = pendulum.parse(
            str(adate_raw.start), exact=True, tz=pendulum.timezone(str(timezone)))
        if isinstance(adate_raw, pendulum.DateTime):
            return ADate(None, adate_raw.in_timezone(UTC))
        else:
            return ADate(adate_raw, None)

    def to_notion(self, timezone: Timezone) -> NotionDate:
        """Transform a date to a Notion representation."""
        if self._the_datetime is not None:
            return NotionDate(self._the_datetime, timezone=str(timezone))
        else:
            return NotionDate(self._surely_the_date)

    def to_db(self) -> datetime.datetime:
        """Transform a timestamp to a DB representation."""
        if self._the_datetime is not None:
            return cast(datetime.datetime, self._the_datetime)
        else:
            return datetime.datetime(
                self._surely_the_date.year, self._surely_the_date.month, self._surely_the_date.day, tzinfo=UTC)

    @staticmethod
    def to_user_str(timezone: Timezone, adate: Optional['ADate']) -> str:
        """Transform a date to something meaningful to a user."""
        # pylint: disable=protected-access
        if not adate:
            return ""
        if adate._the_datetime is not None:
            return cast(str, adate._the_datetime.in_timezone(pendulum.timezone(str(timezone))).to_datetime_string())
        else:
            return cast(str, adate._surely_the_date.to_date_string())

    def subtract_days(self, days_cnt: int) -> 'ADate':
        """Subtract these number of days from this date."""
        if self._the_datetime is not None:
            return ADate.from_date_and_time(self._the_datetime.subtract(days=days_cnt))
        else:
            return ADate.from_date(self._surely_the_date.subtract(days=days_cnt))

    def start_of_day(self) -> 'ADate':
        """The start of the day."""
        if self._the_datetime is not None:
            return ADate.from_date_and_time(self._the_datetime.start_of("day"))
        else:
            return self

    def end_of_day(self) -> 'ADate':
        """The end of the day."""
        if self._the_datetime is not None:
            return ADate.from_date_and_time(self._the_datetime.end_of("day"))
        else:
            return self

    def next_day(self) -> 'ADate':
        """Return the next day for a date."""
        if self._the_datetime is not None:
            return ADate.from_date_and_time(self._the_datetime.add(days=1))
        else:
            return ADate.from_date(self._surely_the_date.add(days=1))

    @property
    def year(self) -> int:
        """The year."""
        if self._the_datetime is not None:
            return cast(int, self._the_datetime.year)
        else:
            return cast(int, self._surely_the_date.year)

    @property
    def month(self) -> int:
        """The month."""
        if self._the_datetime is not None:
            return cast(int, self._the_datetime.month)
        else:
            return cast(int, self._surely_the_date.month)

    @property
    def day(self) -> int:
        """The day."""
        if self._the_datetime is not None:
            return cast(int, self._the_datetime.day)
        else:
            return cast(int, self._surely_the_date.day)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, ADate):
            raise Exception(f"Cannot compare an ADate name with {other.__class__.__name__}")

        if self._the_datetime is not None:
            if other._the_datetime is not None:
                return cast(bool, self._the_datetime < other._the_datetime)
            else:
                return cast(
                    bool,
                    self._the_datetime < pendulum.DateTime(
                        other._surely_the_date.year, other._surely_the_date.month,
                        other._surely_the_date.day, tzinfo=UTC))
        else:
            if other._the_datetime is not None:
                return cast(
                    bool,
                    pendulum.DateTime(
                        self._surely_the_date.year, self._surely_the_date.month,
                        self._surely_the_date.day, tzinfo=UTC) < other._the_datetime)
            else:
                return cast(bool, self._surely_the_date < other._surely_the_date)

    def __str__(self) -> str:
        """Transform this to a string version."""
        if self._the_datetime is not None:
            return cast(str, self._the_datetime.to_datetime_string())
        else:
            return cast(str, self._surely_the_date.to_date_string())

    @property
    def _surely_the_date(self) -> pendulum.Date:
        if self._the_date is None:
            raise Exception("Something bad has happened")
        return self._the_date
