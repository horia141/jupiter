"""An timezone in this domain."""
from functools import total_ordering
from typing import Optional, cast

import pendulum
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import AtomicValue, Value, value
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone


@value
@total_ordering
class Timezone(AtomicValue):
    """A timezone in this domain."""

    the_timezone: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_timezone = self._clean_the_timezone(self.the_timezone)

    @staticmethod
    def from_raw(timezone_raw: Optional[str]) -> "Timezone":
        """Validate and clean a timezone."""
        if not timezone_raw:
            raise InputValidationError("Expected timezone to be non-null")

        return Timezone(Timezone._clean_the_timezone(timezone_raw))

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Timezone):
            raise Exception(
                f"Cannot compare a timezone with {other.__class__.__name__}",
            )
        return self.the_timezone < other.the_timezone

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_timezone

    @staticmethod
    def _clean_the_timezone(timezone_raw: str) -> str:
        timezone_str: str = timezone_raw.strip()

        try:
            return cast(str, pendulum.tz.timezone(timezone_str).name)
        except InvalidTimezone as err:
            raise InputValidationError(f"Invalid timezone '{timezone_raw}'") from err


UTC = Timezone.from_raw("UTC")
