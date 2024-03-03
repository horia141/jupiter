"""An timezone in this domain."""
from functools import total_ordering
from typing import cast

import pendulum
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone


@value
@total_ordering
class Timezone(AtomicValue[str]):
    """A timezone in this domain."""

    the_timezone: str

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


class TimezoneDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[Timezone]):
    """Encode to a database primitive."""

    def to_primitive(self, value: Timezone) -> Primitive:
        """Encode to a database primitive."""
        return value.the_timezone


class TimezoneDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[Timezone]):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> Timezone:
        """Decode from a raw string."""
        timezone_str: str = value.strip()

        try:
            return Timezone(cast(str, pendulum.tz.timezone(timezone_str).name))
        except InvalidTimezone as err:
            raise InputValidationError(f"Invalid timezone '{value}'") from err


UTC = Timezone("UTC")
