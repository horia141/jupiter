from enum import Enum


class EventSource(str, Enum):
    CLI = "cli"
    EMAIL = "email"
    GC_CRON = "gc-cron"
    GEN_CRON = "gen-cron"
    SLACK = "slack"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
