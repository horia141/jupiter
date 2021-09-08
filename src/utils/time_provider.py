"""A source of time, kept constant across each request."""
from typing import Final

import pendulum
from pendulum import UTC, Date

from domain.common.timestamp import Timestamp


class TimeProvider:
    """A source of time, kept constant across each request."""

    _right_now: Final[Timestamp]

    def __init__(self) -> None:
        """Constructor."""
        self._right_now = Timestamp(pendulum.now(tz=UTC))

    def get_current_date(self) -> pendulum.Date:
        """Get the current date."""
        return Date(self._right_now.value.year, self._right_now.value.month, self._right_now.value.day)  # pylint: disable=no-member

    def get_current_time(self) -> Timestamp:
        """Get the current time."""
        return self._right_now
