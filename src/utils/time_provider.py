"""A source of time, kept constant across each request."""
from typing import Final

import pendulum


class TimeProvider:
    """A source of time, kept constant across each request."""

    _right_now: Final[pendulum.DateTime]

    def __init__(self) -> None:
        """Constructor."""
        self._right_now = pendulum.now(tz="UTC")

    def get_current_time(self) -> pendulum.DateTime:
        """Get the current time."""
        return self._right_now
