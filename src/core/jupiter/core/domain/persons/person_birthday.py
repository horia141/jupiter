"""The birthday of a person."""
from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, Tuple

from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value


@dataclass(eq=True, unsafe_hash=True)
class PersonBirthday(Value):
    """The birthday of a person."""

    _MONTH_NAME_INDEX: ClassVar[Dict[str, int]] = {
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
    _MONTH_INDEX_NAME: ClassVar[Dict[int, str]] = {
        i: n for (n, i) in _MONTH_NAME_INDEX.items()
    }

    day: int
    month: int

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        day, month = self._clean_the_day_and_month(self.day, self.month)
        self.day = day
        self.month = month

    @staticmethod
    def from_raw(birthday_str: Optional[str]) -> "PersonBirthday":
        """Validate and clean a raw birthday given as 12 May."""
        if not birthday_str:
            raise InputValidationError("Expected birthday to be non null")

        parts = birthday_str.strip().split(" ")
        if len(parts) != 2:
            raise InputValidationError(f"Invalid format for birthday '{birthday_str}'")

        try:
            day = RecurringTaskDueAtDay.from_raw(
                RecurringTaskPeriod.MONTHLY,
                int(parts[0], base=10),
            )
            month = PersonBirthday._MONTH_NAME_INDEX[parts[1].capitalize()]
        except ValueError as err:
            raise InputValidationError(
                f"Invalid format for day part of birthday '{birthday_str}'",
            ) from err
        except KeyError as err:
            raise InputValidationError(
                f"Invalid format for month part of birthday '{birthday_str}'",
            ) from err

        return PersonBirthday(day.as_int(), month)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.day} {self._MONTH_INDEX_NAME[self.month]}"

    @staticmethod
    def _clean_the_day_and_month(day: int, month: int) -> Tuple[int, int]:
        _ = RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.MONTHLY, day)
        if month < 1 or month > 12:
            raise InputValidationError(f"Month is out of bounds with value {month}")
        return day, month
