"""A source of time, kept constant across each request."""
from typing import Final

import pendulum
from pendulum import UTC

from jupiter.framework.base.timestamp import Timestamp


class TimeProvider:
    """A source of time, kept constant across each request."""

    _right_now: Final[Timestamp]

    def __init__(self) -> None:
        """Constructor."""
        self._right_now = Timestamp(pendulum.now(tz=UTC))

    def get_current_time(self) -> Timestamp:
        """Get the current time."""
        return self._right_now
