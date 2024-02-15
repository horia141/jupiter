"""A date or possibly a datetime for the application."""
from datetime import date, datetime
from functools import total_ordering
from typing import Optional, cast

import pendulum
import pendulum.parser
import pendulum.parsing
import pendulum.tz
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.realm import (
    DatabaseRealm,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
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
    def from_date(date: Date | date) -> "ADate":
        """Construct an ADate from a date."""
        return ADate(Date(date.year, date.month, date.day))

    @staticmethod
    def from_str(date_raw: str) -> "ADate":
        """Parse a date from string."""
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

    def subtract_days(self, days_cnt: int) -> "ADate":
        """Subtract these number of days from this date."""
        return ADate.from_date(self.the_date.subtract(days=days_cnt))

    def next_day(self) -> "ADate":
        """Return the next day for a date."""
        return ADate.from_date(self.the_date.add(days=1))

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
        return date(
            value.the_date.year,
            value.the_date.month,
            value.the_date.day,
        )


class ADateDatabaseDecoder(RealmDecoder[ADate, DatabaseRealm]):
    """A decoder for adates in databases."""

    def decode(self, value: RealmThing) -> ADate:
        if not isinstance(value, (date, Date)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be datetime or DateTime"
            )

        return ADate.from_date(value)
