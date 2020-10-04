"""A source of time, kept constant across each request."""
from typing import Final

import pendulum
from pendulum import UTC, Date

from models.basic import Timestamp


class TimeProvider:
    """A source of time, kept constant across each request."""

    _right_now: Final[Timestamp]

    def __init__(self) -> None:
        """Constructor."""
        self._right_now = Timestamp(pendulum.now(tz=UTC))

    def get_current_date(self) -> pendulum.Date:
        """Get the current date."""
        return Date(self._right_now.year, self._right_now.month, self._right_now.day)  # pylint: disable=no-member

    def get_current_time(self) -> Timestamp:
        """Get the current time."""
        return self._right_now
