"""The source of the note."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class NoteDomain(EnumValue):
    """The source of a note."""

    INBOX_TASK = "inbox-task"
    WORKING_MEM = "working-mem"
    TIME_PLAN = "time-plan"
    SCHEDULE_STREAM = "schedule-stream"
    SCHEDULE_EVENT_IN_DAY = "schedule-event-in-day"
    SCHEDULE_EVENT_FULL_DAYS = "schedule-event-full-days"
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
