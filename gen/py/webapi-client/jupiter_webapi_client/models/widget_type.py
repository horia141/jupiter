from enum import Enum


class WidgetType(str, Enum):
    CALENDAR_DAY = "calendar-day"
    CHORE_INBOX_TASKS = "chore-inbox-tasks"
    GAMIFICATION_HISTORY_MONTHLY = "gamification-history-monthly"
    GAMIFICATION_HISTORY_WEEKLY = "gamification-history-weekly"
    GAMIFICATION_OVERVIEW = "gamification-overview"
    HABIT_INBOX_TASKS = "habit-inbox-tasks"
    KEY_BIG_PLANS_PROGRESS = "key-big-plans-progress"
    KEY_HABITS_STREAKS = "key-habits-streaks"
    MOTD = "motd"
    RANDOM_CHORE = "random-chore"
    RANDOM_HABIT = "random-habit"
    SCHEDULE_DAY = "schedule-day"
    TIME_PLAN_VIEW = "time-plan-view"
    UPCOMING_BIRTHDAYS = "upcoming-birthdays"
    WORKING_MEM = "working-mem"

    def __str__(self) -> str:
        return str(self.value)
