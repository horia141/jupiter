"""A source of time, kept constant across each request."""
from typing import Final

import pendulum
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.timestamp import Timestamp
from pendulum import UTC


class TimeProvider:
    """A source of time, kept constant for the lifetime of this object."""

    _right_now: Final[Timestamp]

    def __init__(self) -> None:
        """Constructor."""
        self._right_now = Timestamp(pendulum.now(tz=UTC))

    def get_current_time(self) -> Timestamp:
        """Get the current time."""
        return self._right_now

    def get_current_date(self) -> ADate:
        """Get the current date."""
        return ADate.from_date(self._right_now.as_date())
