from enum import Enum


class MetricUnit(str, Enum):
    COUNT = "count"
    MONEY = "money"
    WEIGHT = "weight"

    def __str__(self) -> str:
        return str(self.value)
