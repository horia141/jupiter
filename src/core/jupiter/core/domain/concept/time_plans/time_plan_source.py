"""The source of a time plan."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanSource(EnumValue):
    """The source of a time plan."""

    USER = "user"
    GENERATED = "generated"
