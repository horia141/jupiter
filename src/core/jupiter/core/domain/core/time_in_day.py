"""The time in hh:mm format."""
from functools import total_ordering

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseEncoder


@hashable_value
@total_ordering
class TimeInDay(AtomicValue[str]):
    """The time in hh:mm format."""

    hour: int
    minute: int

    @staticmethod
    def from_parts(hour: int, minute: int) -> "TimeInDay":
        """Construct from parts."""
        if hour < 0 or hour > 23:
            raise InputValidationError(f"Invalid hour: {hour}")
        if minute < 0 or minute > 59:
            raise InputValidationError(f"Invalid minute: {minute}")
        return TimeInDay(hour=hour, minute=minute)

    def __str__(self) -> str:
        """Convert to a string."""
        return f"{self.hour:02d}:{self.minute:02d}"

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, TimeInDay):
            raise Exception(
                f"Cannot compare with {other.__class__.__name__}",
            )

        if self.hour < other.hour:
            return True
        if self.hour > other.hour:
            return False

        return self.minute < other.minute


class TimeInDayDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[TimeInDay]):
    """Encode to a database primitive."""

    def to_primitive(self, value: TimeInDay) -> str:
        """Encode to a database primitive."""
        return str(value)


class TimeInDayDatabaseDecoder(PrimitiveAtomicValueDatabaseEncoder[TimeInDay]):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> TimeInDay:
        """Decode from a raw string."""
        parts = value.split(":")
        if len(parts) != 2:
            raise InputValidationError(f"Invalid time: {value}")
        try:
            return TimeInDay.from_parts(int(parts[0]), int(parts[1]))
        except ValueError as err:
            raise InputValidationError(f"Invalid time: {value}") from err
