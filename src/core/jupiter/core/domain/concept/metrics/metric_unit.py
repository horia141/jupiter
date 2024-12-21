"""The unit for a metric."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class MetricUnit(EnumValue):
    """The unit for a metric."""

    COUNT = "count"
    MONETARY_AMOUNT = "money"
    WEIGHT = "weight"
