"""The source of the note."""


from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class NoteDomain(EnumValue):
    """The source of a note."""

    INBOX_TASK = "inbox-task"
    HABIT = "habit"
    CHORE = "chore"
    BIG_PLAN = "big-plan"
    DOC = "doc"
    JOURNAL = "journal"
    VACATION = "vacation"
    PROJECT = "project"
    SMART_LIST = "smart-list"
    SMART_LIST_ITEM = "smart-list-item"
    METRIC = "metric"
    METRIC_ENTRY = "metric-entry"
    PERSON = "person"
