from enum import Enum


class WidgetType(str, Enum):
    CALENDAR_DAY = "calendar-day"
    HABIT_INBOX_TASKS = "habit-inbox-tasks"
    KEY_HABITS_STREAKS = "key-habits-streaks"
    MOTD = "motd"
    WORKING_MEM = "working-mem"

    def __str__(self) -> str:
        return str(self.value)
