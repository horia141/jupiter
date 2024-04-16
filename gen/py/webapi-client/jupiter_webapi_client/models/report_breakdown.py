from enum import Enum


class ReportBreakdown(str, Enum):
    BIG_PLANS = "big-plans"
    CHORES = "chores"
    GLOBAL = "global"
    HABITS = "habits"
    PERIODS = "periods"
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
