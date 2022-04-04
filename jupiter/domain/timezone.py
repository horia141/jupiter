"""An timezone in this domain."""
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

import pendulum
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
@total_ordering
class Timezone(Value):
    """An timezone in this domain."""

    _the_timezone: str

    @staticmethod
    def from_raw(timezone_raw: Optional[str]) -> 'Timezone':
        """Validate and clean a timezone."""
        if not timezone_raw:
            raise InputValidationError("Expected timezone to be non-null")

        timezone_str: str = timezone_raw.strip()

        try:
            return Timezone(pendulum.timezone(timezone_str).name)
        except InvalidTimezone as err:
            raise InputValidationError(f"Invalid timezone '{timezone_raw}'") from err

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Timezone):
            raise Exception(f"Cannot compare an TIMEZONE {other.__class__.__name__}")
        return self._the_timezone < other._the_timezone

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_timezone


UTC = Timezone.from_raw("UTC")
