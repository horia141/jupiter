"""A time provider which can provide a per-request time."""
from contextvars import ContextVar

import pendulum
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.utils.time_provider import TimeProvider
from pendulum.tz.timezone import UTC

_RIGHT_NOW: ContextVar[Timestamp | None] = ContextVar(
    "time_provider_right_now", default=None
)


class PerRequestTimeProvider(TimeProvider):
    """A source of time, kept constant across each request."""

    def set_request_time(self) -> None:
        """Prepare the time provider so that there is a time for the whole request."""
        _RIGHT_NOW.set(Timestamp(pendulum.now(tz=UTC)))

    def get_current_time(self) -> Timestamp:
        """Get the current time."""
        right_now = _RIGHT_NOW.get()
        if right_now is None:
            raise Exception("Invalid time provider state")
        return right_now
