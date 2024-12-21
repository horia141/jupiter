"""A date or possibly a datetime for the application."""
from datetime import date
from functools import total_ordering
from typing import cast

import pendulum
import pendulum.parser
import pendulum.parsing
import pendulum.tz
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import (
    CliRealm,
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
    WebRealm,
)
from jupiter.core.framework.value import AtomicValue, hashable_value
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC


@hashable_value
@total_ordering
class ADate(AtomicValue[Date]):
    """A date or possibly a datetime for the application."""

    the_date: Date

    @staticmethod
    def from_components(year: int, month: int, day: int) -> "ADate":
        """Construct an ADate from its components."""
        return ADate(Date(year, month, day))

    @staticmethod
    def from_timestamp(timestamp: Timestamp) -> "ADate":
        """Construct an ADate from a timestamp."""
        return ADate(timestamp.as_date())

    @staticmethod
    def from_date(date: Date | date) -> "ADate":
        """Construct an ADate from a date."""
        try:
            return ADate(Date(date.year, date.month, date.day))
        except ValueError as err:
            raise InputValidationError(f"Invalid date because: {err}") from None

    @staticmethod
    def from_str(date_raw: str) -> "ADate":
        """Parse a date from string."""
        try:
            return ADate(
                cast(
                    Date,
                    pendulum.parser.parse(
                        date_raw.replace(" 00:00:00", ""),
                        tz=UTC,
                        exact=True,
                    ),
                ),
            )
        except ValueError as err:
            raise InputValidationError(f"Invalid date because: {err}") from None

    def to_timestamp_at_start_of_day(self) -> Timestamp:
        """Transform to a timetamp at the start of the day."""
        return Timestamp.from_date_and_time(
            DateTime(
                self.the_date.year,
                self.the_date.month,
                self.the_date.day,
                tzinfo=UTC,
            ).start_of("day"),
        )

    def to_timestamp_at_end_of_day(self) -> Timestamp:
        """Transform to a timestamp at the end of the day."""
        return Timestamp.from_date_and_time(
            DateTime(
                self.the_date.year,
                self.the_date.month,
                self.the_date.day,
                tzinfo=UTC,
            ).end_of("day"),
        )

    def add_days(self, days_cnt: int) -> "ADate":
        """Add these number of days to this date."""
        return ADate.from_date(self.the_date.add(days=days_cnt))

    def subtract_days(self, days_cnt: int) -> "ADate":
        """Subtract these number of days from this date."""
        return ADate.from_date(self.the_date.subtract(days=days_cnt))

    def next_day(self) -> "ADate":
        """Return the next day for a date."""
        return ADate.from_date(self.the_date.add(days=1))

    def days_since(self, other: "ADate") -> int:
        """Return the number of days between this and another date."""
        return cast(int, self.the_date.diff(other.the_date).in_days())

    @property
    def year(self) -> int:
        """The year."""
        return self.the_date.year

    @property
    def month(self) -> int:
        """The month."""
        return self.the_date.month

    @property
    def day(self) -> int:
        """The day."""
        return self.the_date.day

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, ADate):
            raise Exception(
                f"Cannot compare an ADate name with {other.__class__.__name__}",
            )

        return cast(bool, self.the_date < other.the_date)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return cast(str, self.the_date.to_date_string())


class ADateDatabaseEncoder(RealmEncoder[ADate, DatabaseRealm]):
    """An encoder for adates in databases."""

    def encode(self, value: ADate) -> RealmThing:
        """Encode to a database realm."""
        return date(
            value.the_date.year,
            value.the_date.month,
            value.the_date.day,
        )


class ADateDatabaseDecoder(RealmDecoder[ADate, DatabaseRealm]):
    """A decoder for adates in databases."""

    def decode(self, value: RealmThing) -> ADate:
        """Decode from a database realm."""
        if not isinstance(value, (str, date, Date)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be date or Date but was {value.__class__}"
            )

        if isinstance(value, str):
            return ADate.from_str(value)
        return ADate.from_date(value)


class ADateCliDecoder(RealmDecoder[ADate, CliRealm]):
    """A decoder for adates in databases."""

    def decode(self, value: RealmThing) -> ADate:
        """Decode from a cli realm."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for str to be date or Date but was {value.__class__}"
            )

        return ADate.from_str(value)


class ADateWebDecoder(RealmDecoder[ADate, WebRealm]):
    """A decoder for adates in databases."""

    def decode(self, value: RealmThing) -> ADate:
        """Decode from a web realm."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for str to be date or Date but was {value.__class__}"
            )

        return ADate.from_str(value)
