"""The source of a time plan."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class TimePlanSource(EnumValue):
    """The source of a time plan."""

    USER = "user"
    GENERATED = "generated"

    @property
    def allow_user_changes(self) -> bool:
        """Whether the user can change the time plan."""
        # Keep synced with ts:time-plan-source.ts
        return self == TimePlanSource.USER
