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
class ADate(AtomicValue[Date | DateTime]):
    """A date or possibly a datetime for the application."""

    the_date: Optional[Date] = None
    the_datetime: Optional[DateTime] = None

    @staticmethod
    def from_date(date: Date) -> "ADate":
        """Construct an ADate from a date."""
        return ADate(date, None)

    @staticmethod
    def from_date_and_time(date_and_time: DateTime) -> "ADate":
        """Construct an ADate from a datetime."""
        return ADate(None, date_and_time)

    def to_timestamp_at_end_of_day(self) -> Timestamp:
        """Transform to a timestamp at the end of the day."""
        if self.the_datetime is not None:
            return Timestamp.from_date_and_time(self.the_datetime.end_of("day"))
        else:
            return Timestamp.from_date_and_time(
                DateTime(
                    self._surely_the_date.year,
                    self._surely_the_date.month,
                    self._surely_the_date.day,
                    tzinfo=UTC,
                ).end_of("day"),
            )

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
            None,
        )

    @staticmethod
    def to_user_str(timezone: Timezone, adate: Optional["ADate"]) -> str:
        """Transform a date to something meaningful to a user."""
        if not adate:
            return ""
        if adate.the_datetime is not None:
            return cast(
                str,
                adate.the_datetime.in_timezone(
                    pendulum.tz.timezone(str(timezone)),
                ).to_iso8601_string(),
            )
        else:
            return cast(str, adate._surely_the_date.to_date_string())

    @staticmethod
    def to_user_date_str(adate: Optional["ADate"]) -> str:
        """Transform a date to something meaningful to a user as a date."""
        if not adate:
            return ""
        if adate.the_datetime is not None:
            return cast(str, adate.the_datetime.to_date_string())
        else:
            return cast(str, adate._surely_the_date.to_date_string())

    def subtract_days(self, days_cnt: int) -> "ADate":
        """Subtract these number of days from this date."""
        if self.the_datetime is not None:
            return ADate.from_date_and_time(self.the_datetime.subtract(days=days_cnt))
        else:
            return ADate.from_date(self._surely_the_date.subtract(days=days_cnt))

    def start_of_day(self) -> "ADate":
        """The start of the day."""
        if self.the_datetime is not None:
            return ADate.from_date_and_time(self.the_datetime.start_of("day"))
        else:
            return self

    def end_of_day(self) -> "ADate":
        """The end of the day."""
        if self.the_datetime is not None:
            return ADate.from_date_and_time(self.the_datetime.end_of("day"))
        else:
            return self

    def next_day(self) -> "ADate":
        """Return the next day for a date."""
        if self.the_datetime is not None:
            return ADate.from_date_and_time(self.the_datetime.add(days=1))
        else:
            return ADate.from_date(self._surely_the_date.add(days=1))

    @property
    def year(self) -> int:
        """The year."""
        if self.the_datetime is not None:
            return cast(int, self.the_datetime.year)
        else:
            return cast(int, self._surely_the_date.year)

    @property
    def month(self) -> int:
        """The month."""
        if self.the_datetime is not None:
            return cast(int, self.the_datetime.month)
        else:
            return cast(int, self._surely_the_date.month)

    @property
    def day(self) -> int:
        """The day."""
        if self.the_datetime is not None:
            return cast(int, self.the_datetime.day)
        else:
            return cast(int, self._surely_the_date.day)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, ADate):
            raise Exception(
                f"Cannot compare an ADate name with {other.__class__.__name__}",
            )

        if self.the_datetime is not None:
            if other.the_datetime is not None:
                return cast(bool, self.the_datetime < other.the_datetime)
            else:
                return cast(
                    bool,
                    self.the_datetime
                    < DateTime(
                        other._surely_the_date.year,
                        other._surely_the_date.month,
                        other._surely_the_date.day,
                        tzinfo=UTC,
                    ),
                )
        else:
            if other.the_datetime is not None:
                return cast(
                    bool,
                    DateTime(
                        self._surely_the_date.year,
                        self._surely_the_date.month,
                        self._surely_the_date.day,
                        tzinfo=UTC,
                    )
                    < other.the_datetime,
                )
            else:
                return cast(bool, self._surely_the_date < other._surely_the_date)

    def __str__(self) -> str:
        """Transform this to a string version."""
        if self.the_datetime is not None:
            return cast(str, self.the_datetime.to_datetime_string())
        else:
            return cast(str, self._surely_the_date.to_date_string())

    @property
    def _surely_the_date(self) -> Date:
        if self.the_date is None:
            raise Exception("Something bad has happened")
        return self.the_date


class ADateDatabaseEncoder(RealmEncoder[ADate, DatabaseRealm]):
    """An encoder for adates in databases."""

    def encode(self, value: ADate) -> RealmThing:
        if value.the_datetime is not None:
            return cast(datetime, value.the_datetime)
        else:
            return datetime(
                value._surely_the_date.year,
                value._surely_the_date.month,
                value._surely_the_date.day,
                tzinfo=UTC,
            )


class ADateDatabaseDecoder(RealmDecoder[ADate, DatabaseRealm]):
    """A decoder for adates in databases."""

    def decode(self, value: RealmThing) -> ADate:
        if not isinstance(value, (datetime, DateTime, date, Date)):
            raise RealmDecodingError(
                f"Expected value for {self.__class__} to be datetime or DateTime"
            )

        if isinstance(value, datetime) and (
            value.hour > 0 or value.minute > 0 or value.second > 0
        ):
            return ADate(None, pendulum.instance(value).in_timezone(UTC))
        else:
            return ADate(
                Date(value.year, value.month, value.day),
                None,
            )
