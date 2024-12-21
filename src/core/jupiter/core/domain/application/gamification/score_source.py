"""The source of a score."""


from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class ScoreSource(EnumValue):
    """The source of a score."""

    INBOX_TASK = "inbox-task"
    BIG_PLAN = "big-plan"
