"""A date or possibly a datetime for the application."""
import datetime
from functools import total_ordering
from typing import Optional, cast

import pendulum
import pendulum.parser
import pendulum.parsing
import pendulum.tz
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC


@hashable_value
@total_ordering
class ADate(AtomicValue):
    """A date or possibly a datetime for the application."""

    the_date: Optional[Date] = None
    the_datetime: Optional[DateTime] = None

    def __post_init_post_parse__(self) -> None:
        """Validate after pydantic construction."""
        # When reconstructing automatically this might happen!
        if isinstance(self.the_date, (datetime.date, datetime.datetime)):
            self.the_date = Date(
                self.the_date.year,
                self.the_date.month,
                self.the_date.day,
            )
        elif isinstance(self.the_datetime, datetime.datetime):
            self.the_datetime = pendulum.instance(self.the_datetime)

    @staticmethod
    def from_date(date: Date) -> "ADate":
        """Construct an ADate from a date."""
        return ADate(date, None)

    @staticmethod
    def from_date_and_time(date_and_time: DateTime) -> "ADate":
        """Construct an ADate from a datetime."""
        return ADate(None, date_and_time)

    @staticmethod
    def from_timestamp(timestamp: Timestamp) -> "ADate":
        """Construct an ADate from a timestamp."""
        return ADate(None, timestamp.value)

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
    def from_raw_in_tz(timezone: Timezone, datetime_raw: Optional[str]) -> "ADate":
        """Validate and clean an ADate."""
        if not datetime_raw:
            raise InputValidationError("Expected datetime to be non-null")

        try:
            adate = pendulum.parser.parse(
                datetime_raw,
                tz=pendulum.tz.timezone(str(timezone)),
                exact=True,
            )

            if isinstance(adate, DateTime):
                return ADate(None, adate.in_timezone(UTC))
            elif isinstance(adate, Date):
                return ADate(adate, None)
            else:
                raise InputValidationError(
                    f"Expected datetime '{datetime_raw}' to be in a proper datetime format",
                )
        except pendulum.parsing.exceptions.ParserError as error:
            raise InputValidationError(
                f"Expected datetime '{datetime_raw}' to be in a proper format",
            ) from error

    @classmethod
    def from_raw(cls, value: Primitive) -> "ADate":
        """Validate and clean an ADate."""
        if not isinstance(value, (str, Date, DateTime)):
            raise InputValidationError(
                "Expected datetime to be string or a date or a datetime"
            )

        if isinstance(value, DateTime):
            return ADate.from_date_and_time(value)
        elif isinstance(value, Date):
            return ADate.from_date(value)

        try:
            adate = pendulum.parser.parse(
                value,
                tz=pendulum.tz.timezone(str(UTC)),
                exact=True,
            )

            if isinstance(adate, DateTime):
                return ADate(None, adate.in_timezone(UTC))
            elif isinstance(adate, Date):
                return ADate(adate, None)
            else:
                raise InputValidationError(
                    f"Expected datetime '{value}' to be in a proper datetime format",
                )
        except pendulum.parsing.exceptions.ParserError as error:
            raise InputValidationError(
                f"Expected datetime '{value}' to be in a proper format",
            ) from error

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
    def from_db(timestamp_raw: datetime.datetime | datetime.date) -> "ADate":
        """Parse a timestamp from a DB representation."""
        if isinstance(timestamp_raw, datetime.datetime) and (
            timestamp_raw.hour > 0
            or timestamp_raw.minute > 0
            or timestamp_raw.second > 0
        ):
            return ADate(None, pendulum.instance(timestamp_raw).in_timezone(UTC))
        else:
            return ADate(
                Date(timestamp_raw.year, timestamp_raw.month, timestamp_raw.day),
                None,
            )

    def to_primitive(self) -> Primitive:
        """Get the primitive representation of this value."""
        if self.the_datetime is not None:
            return cast(DateTime, self.the_datetime)
        else:
            return cast(Date, self._surely_the_date)

    def to_db(self) -> datetime.datetime:
        """Transform a timestamp to a DB representation."""
        if self.the_datetime is not None:
            return cast(datetime.datetime, self.the_datetime)
        else:
            return datetime.datetime(
                self._surely_the_date.year,
                self._surely_the_date.month,
                self._surely_the_date.day,
                tzinfo=UTC,
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

    def just_the_date(self) -> "ADate":
        """Just the date part."""
        if self.the_datetime is not None:
            return ADate.from_date(self.the_datetime.date())
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
