"""A timestamp in the application."""
import datetime
from functools import total_ordering
from typing import cast

import pendulum
import pendulum.parser
import pendulum.parsing
import pendulum.tz
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
class Timestamp(AtomicValue[datetime.datetime]):
    """A timestamp in the application."""

    the_ts: DateTime

    @staticmethod
    def from_date_and_time(date_and_time: DateTime) -> "Timestamp":
        """Construct a Timestamp from a datetime object."""
        return Timestamp(date_and_time.in_timezone(tz=UTC))

    @staticmethod
    def from_unix_timestamp(unix_timestamp: int) -> "Timestamp":
        """Construct a Timestamp from a unix timestamp."""
        return Timestamp(pendulum.from_timestamp(unix_timestamp, tz=UTC))

    def as_date(self) -> Date:
        """The raw date of the timestamp."""
        return cast(Date, self.the_ts.date())  # type: ignore

    def mins_since(self, other: "Timestamp") -> int:
        """Get the minutes since another timestamp."""
        return cast(int, self.the_ts.diff(other.the_ts).in_minutes())  # type: ignore

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
        """Encode to a database realm."""
        return value.the_ts


class TimestampDatabaseDecoder(RealmDecoder[Timestamp, DatabaseRealm]):
    """A decoder for timestamps in databases."""

    def decode(self, value: RealmThing) -> Timestamp:
        """Decode from a database realm."""
        if not isinstance(value, (str, datetime.date, datetime.datetime, DateTime)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be datetime or DateTime but was {value.__class__}"
            )

        if isinstance(value, str):
            raw_dt = pendulum.parser.parse(value, tz=UTC, exact=True)
            if not isinstance(raw_dt, DateTime):
                raise RealmDecodingError(
                    f"Expected value for {self.__class__} to be datetime or DateTime but was parsed as {raw_dt.__class__}"
                )
            return Timestamp.from_date_and_time(raw_dt)
        elif isinstance(value, DateTime):
            return Timestamp.from_date_and_time(value)
        elif isinstance(value, datetime.datetime):
            return Timestamp(pendulum.instance(value).in_timezone(UTC))
        elif isinstance(value, datetime.date):
            return Timestamp(
                pendulum.datetime(value.year, value.month, value.day, tz=UTC)
            )
