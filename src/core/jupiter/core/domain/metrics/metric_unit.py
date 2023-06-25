"""The unit for a metric."""
import enum
from functools import lru_cache
from typing import Iterable, Optional

from jupiter.core.framework.errors import InputValidationError


@enum.unique
class MetricUnit(enum.Enum):
    """The unit for a metric."""

    COUNT = "count"
    MONETARY_AMOUNT = "money"
    WEIGHT = "weight"

    @staticmethod
    def from_raw(metric_unit_raw: Optional[str]) -> "MetricUnit":
        """Validate and clean an metric unit."""
        if not metric_unit_raw:
            raise InputValidationError("Expected metric unit to be non-null")

        metric_unit_str: str = "-".join(metric_unit_raw.strip().lower().split(" "))

        if metric_unit_str not in MetricUnit.all_values():
            raise InputValidationError(
                f"Expected metric unit '{metric_unit_raw}' to be "
                + f"one of '{','.join(MetricUnit.all_values())}'",
            )

        return MetricUnit(metric_unit_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for metric units."""
        return frozenset(mu.value for mu in MetricUnit)

    def to_nice(self) -> str:
        """A prettier version of the value."""
        return str(self.value).capitalize()
