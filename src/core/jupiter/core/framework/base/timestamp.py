"""A timestamp in the application."""
import datetime
from functools import total_ordering
from typing import cast

import pendulum
import pendulum.parser
import pendulum.parsing
import pendulum.tz
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.value import AtomicValue, value
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC


@value
@total_ordering
class Timestamp(AtomicValue):
    """A timestamp in the application."""

    the_ts: DateTime

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return DateTime

    @staticmethod
    def from_date(date: Date) -> "Timestamp":
        """Construct a Timestamp from a date object."""
        return Timestamp(
            DateTime(  # type: ignore
                year=date.year,
                month=date.month,
                day=date.day,
                tzinfo=UTC,
            ),
        )

    @staticmethod
    def from_date_and_time(date_and_time: DateTime) -> "Timestamp":
        """Construct a Timestamp from a datetime object."""
        return Timestamp(date_and_time.in_timezone(tz=UTC))

    @staticmethod
    def from_unix_timestamp(unix_timestamp: int) -> "Timestamp":
        """Construct a Timestamp from a unix timestamp."""
        return Timestamp(pendulum.from_timestamp(unix_timestamp, tz=UTC))

    @classmethod
    def from_raw(cls, value: Primitive) -> "Timestamp":
        """Validate and clean an optional timestamp."""
        if not isinstance(
            value, (str, datetime.date, datetime.datetime, Date, DateTime)
        ):
            raise RealmDecodingError(
                "Expected timestamp to be string or date or datetime"
            )

        if isinstance(value, DateTime):
            return Timestamp.from_date_and_time(value)
        elif isinstance(value, datetime.datetime):
            return Timestamp.from_db(value)
        elif isinstance(value, Date):
            return Timestamp.from_date(value)
        elif isinstance(value, datetime.date):
            return Timestamp.from_dbx(value)

        try:
            timestamp = pendulum.parser.parse(
                value,
                tz=UTC,
                exact=True,
            )

            if isinstance(timestamp, DateTime):
                timestamp = timestamp.in_timezone(UTC)
            elif isinstance(timestamp, Date):
                timestamp = DateTime(  # type: ignore
                    timestamp.year,
                    timestamp.month,
                    timestamp.day,
                    tzinfo=UTC,
                )
            else:
                raise InputValidationError(
                    f"Expected datetime '{value}' to be in a proper datetime format",
                )

            return Timestamp(timestamp)
        except pendulum.parsing.exceptions.ParserError as error:
            raise RealmDecodingError(
                f"Expected datetime '{value}' to be in a proper format",
            ) from error

    @staticmethod
    def from_str(timestamp_raw: str) -> "Timestamp":
        """Parse a timestamp from a string."""
        timestamp = pendulum.parser.parse(timestamp_raw, tz=UTC, exact=True)
        if not isinstance(timestamp, DateTime):
            raise InputValidationError(
                f"Expected timestamp '{timestamp_raw}' to be in a proper timestamp format",
            )
        return Timestamp(timestamp)

    @staticmethod
    def from_dbx(timestamp_raw: datetime.date) -> "Timestamp":
        """Parse a timestamp from a DB representation."""
        return Timestamp(
            pendulum.datetime(
                timestamp_raw.year, timestamp_raw.month, timestamp_raw.day, tz="UTC"
            )
        )

    @staticmethod
    def from_db(timestamp_raw: datetime.datetime) -> "Timestamp":
        """Parse a timestamp from a DB representation."""
        return Timestamp(pendulum.instance(timestamp_raw).in_timezone(UTC))

    def to_primitive(self) -> Primitive:
        return self.the_ts

    def to_db(self) -> datetime.datetime:
        """Transform a timestamp to a DB representation."""
        return cast(datetime.datetime, self.the_ts)

    def as_datetime(self) -> DateTime:
        """The raw datetime of the timestamp."""
        return self.the_ts

    def as_date(self) -> Date:
        """The raw date of the timestamp."""
        return cast(Date, self.the_ts.date())  # type: ignore

    @property
    def value(self) -> DateTime:
        """The value as a time."""
        return self.the_ts

    @property
    def month(self) -> int:
        """The value of the month."""
        return cast(int, self.value.month)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Timestamp):
            raise Exception(
                f"Cannot compare an tag name with {other.__class__.__name__}",
            )
        return cast(bool, self.the_ts < other.the_ts)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return cast(str, self.the_ts.to_datetime_string())  # type: ignore


class TimestampDatabaseEncoder(RealmEncoder[Timestamp, DatabaseRealm]):
    """An encoder for timestamps in databases."""

    def encode(self, value: Timestamp) -> RealmThing:
        return value.as_datetime()


class TimestampDatabaseDecoder(RealmDecoder[Timestamp, DatabaseRealm]):
    """A decoder for timestamps in databases."""

    def decode(self, value: RealmThing) -> Timestamp:
        if not isinstance(
            value, (str, datetime.date, datetime.datetime, Date, DateTime)
        ):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be primitive"
            )

        return Timestamp.from_raw(value)
