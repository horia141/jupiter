from enum import Enum


class WorkspaceFeature(str, Enum):
    BIG_PLANS = "big-plans"
    CHORES = "chores"
    DOCS = "docs"
    EMAIL_TASKS = "email-tasks"
    HABITS = "habits"
    INBOX_TASKS = "inbox-tasks"
    JOURNALS = "journals"
    METRICS = "metrics"
    PERSONS = "persons"
    PROJECTS = "projects"
    SLACK_TASKS = "slack-tasks"
    SMART_LISTS = "smart-lists"
    VACATIONS = "vacations"
    WORKING_MEM = "working-mem"

    def __str__(self) -> str:
        return str(self.value)