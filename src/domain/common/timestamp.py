"""A timestamp in the application."""
from dataclasses import dataclass
import datetime
from functools import total_ordering
from typing import Optional, cast

import pendulum
from pendulum import UTC

from domain.common.timezone import Timezone
from models.errors import ModelValidationError
from models.frame.value import Value


@total_ordering
@dataclass(frozen=True)
class Timestamp(Value):
    """A timestamp in the application."""

    _the_ts: pendulum.DateTime

    @staticmethod
    def from_date(date: pendulum.Date) -> 'Timestamp':
        """Construct a Timestamp from a date object."""
        return Timestamp(pendulum.DateTime(year=date.year, month=date.month, day=date.day, tzinfo=UTC))

    @staticmethod
    def from_date_and_time(date_and_time: pendulum.DateTime) -> 'Timestamp':
        """Construct a Timestamp from a datetime object."""
        return Timestamp(date_and_time.in_timezone(tz=UTC))

    @staticmethod
    def from_raw(timezone: Timezone, timestamp_raw: Optional[str]) -> 'Timestamp':
        """Validate and clean an optional timestamp."""
        if not timestamp_raw:
            raise ModelValidationError("Expected timestamp to be non-null")

        try:
            timestamp = pendulum.parse(timestamp_raw, tz=pendulum.timezone(str(timezone)), exact=True)

            if isinstance(timestamp, pendulum.DateTime):
                timestamp = timestamp.in_timezone(UTC)
            elif isinstance(timestamp, pendulum.Date):
                timestamp = pendulum.DateTime(timestamp.year, timestamp.month, timestamp.day, tzinfo=UTC)
            else:
                raise ModelValidationError(f"Expected datetime '{timestamp_raw}' to be in a proper datetime format")

            return Timestamp(timestamp)
        except pendulum.parsing.exceptions.ParserError as error:
            raise ModelValidationError(f"Expected datetime '{timestamp_raw}' to be in a proper format") from error

    @staticmethod
    def from_str(timestamp_raw: str) -> 'Timestamp':
        """Parse a timestamp from a string."""
        timestamp = pendulum.parse(timestamp_raw, tz=UTC, exact=True)
        if not isinstance(timestamp, pendulum.DateTime):
            raise ModelValidationError(f"Expected timestamp '{timestamp_raw}' to be in a proper timestamp format")
        return Timestamp(timestamp)

    @staticmethod
    def from_db(timestamp_raw: datetime.datetime) -> 'Timestamp':
        """Parse a timestamp from a DB representation."""
        return Timestamp(pendulum.instance(timestamp_raw).in_timezone(UTC))

    @staticmethod
    def from_notion(timestamp_raw: datetime.datetime) -> 'Timestamp':
        """Parse a timestamp from a Notion representation."""
        return Timestamp(pendulum.instance(timestamp_raw).in_timezone(UTC))

    def to_notion(self, timezone: Timezone) -> datetime.datetime:
        """Transform a timestamp to a Notion representation."""
        return cast(datetime.datetime, self._the_ts.in_timezone(pendulum.timezone(str(timezone))))

    def to_db(self) -> datetime.datetime:
        """Transform a timestamp to a DB representation."""
        return cast(datetime.datetime, self._the_ts)

    @property
    def value(self) -> pendulum.DateTime:
        """The value as a time."""
        return self._the_ts

    @property
    def month(self) -> int:
        """The value of the month."""
        return cast(int, self.value.month)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Timestamp):
            raise Exception(f"Cannot compare an tag name with {other.__class__.__name__}")
        return cast(bool, self._the_ts < other._the_ts)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return cast(str, self._the_ts.to_datetime_string())
