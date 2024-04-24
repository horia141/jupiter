from enum import Enum


class NoteDomain(str, Enum):
    BIG_PLAN = "big-plan"
    CHORE = "chore"
    DOC = "doc"
    HABIT = "habit"
    INBOX_TASK = "inbox-task"
    JOURNAL = "journal"
    METRIC = "metric"
    METRIC_ENTRY = "metric-entry"
    PERSON = "person"
    PROJECT = "project"
    SMART_LIST = "smart-list"
    SMART_LIST_ITEM = "smart-list-item"
    VACATION = "vacation"
    WORKING_MEM = "working-mem"

    def __str__(self) -> str:
        return str(self.value)