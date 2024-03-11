"""The birthday of a person."""
from typing import ClassVar

from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@hashable_value
class PersonBirthday(AtomicValue[str]):
    """The birthday of a person."""

    _MONTH_NAME_INDEX: ClassVar[dict[str, int]] = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    _MONTH_INDEX_NAME: ClassVar[dict[int, str]] = {
        i: n for (n, i) in _MONTH_NAME_INDEX.items()
    }

    day: int
    month: int

    def __init__(self, day: int, month: int) -> None:
        """Construct a new birthday."""
        _ = RecurringTaskDueAtDay(RecurringTaskPeriod.MONTHLY, day)
        if month < 1 or month > 12:
            raise InputValidationError(f"Month is out of bounds with value {month}")
        self.day = day
        self.month = month

    def __str__(self) -> str:
        """String representation."""
        return f"{self.day} {self._MONTH_INDEX_NAME[self.month]}"


class PersonBirthdayDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[PersonBirthday]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: PersonBirthday) -> Primitive:
        """Encode to a primitive."""
        return f"{value.day} {PersonBirthday._MONTH_INDEX_NAME[value.month]}"


class PersonBirthdayDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[PersonBirthday]
):
    """Decode from a database primitive."""

    def from_raw_str(self, primitive: str) -> PersonBirthday:
        """Decode from a raw string."""
        parts = primitive.strip().split(" ")
        if len(parts) != 2:
            raise InputValidationError(f"Invalid format for birthday '{primitive}'")

        try:
            day = RecurringTaskDueAtDay(
                RecurringTaskPeriod.MONTHLY,
                int(parts[0], base=10),
            )
            month = PersonBirthday._MONTH_NAME_INDEX[parts[1].capitalize()]
        except ValueError as err:
            raise InputValidationError(
                f"Invalid format for day part of birthday '{primitive}'",
            ) from err
        except KeyError as err:
            raise InputValidationError(
                f"Invalid format for month part of birthday '{primitive}'",
            ) from err

        return PersonBirthday(day.as_int(), month)
