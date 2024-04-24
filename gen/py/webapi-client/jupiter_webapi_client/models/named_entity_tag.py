from enum import Enum


class NamedEntityTag(str, Enum):
    BIGPLAN = "BigPlan"
    CHORE = "Chore"
    DOC = "Doc"
    EMAILTASK = "EmailTask"
    HABIT = "Habit"
    INBOXTASK = "InboxTask"
    JOURNAL = "Journal"
    METRIC = "Metric"
    METRICENTRY = "MetricEntry"
    PERSON = "Person"
    PROJECT = "Project"
    SLACKTASK = "SlackTask"
    SMARTLIST = "SmartList"
    SMARTLISTITEM = "SmartListItem"
    SMARTLISTTAG = "SmartListTag"
    VACATION = "Vacation"
    WORKINGMEM = "WorkingMem"

    def __str__(self) -> str:
        return str(self.value)