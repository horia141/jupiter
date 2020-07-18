"""Command-level properties."""
from typing import Final

from pendulum.tz.timezone import Timezone


class GlobalProperties:
    """Command-level properties."""

    _timezone: Final[Timezone]

    def __init__(self, timezone: Timezone) -> None:
        """Constructor."""
        self._timezone = timezone

    @property
    def timezone(self) -> Timezone:
        """The global timezone."""
        return self._timezone
