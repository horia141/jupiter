"""What exactly to sync."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class SyncTarget(EnumValue):
    """What exactly to generate, gc, or look at systematically."""

    INBOX_TASKS = "inbox-tasks"
    WORKING_MEM = "working-mem"
    TIME_PLANS = "time-plans"
    SCHEDULES = "schedule"
    HABITS = "habits"
    CHORES = "chores"
    BIG_PLANS = "big-plans"
    JOURNALS = "journals"
    DOCS = "docs"
    VACATIONS = "vacations"
    PROJECTS = "projects"
    SMART_LISTS = "smart-lists"
    METRICS = "metrics"
    PERSONS = "persons"
    SLACK_TASKS = "slack-tasks"
    EMAIL_TASKS = "email-tasks"
