"""The origin of an inbox task."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class InboxTaskSource(EnumValue):
    """The origin of an inbox task."""

    USER = "user"
    WORKING_MEM_CLEANUP = "working-mem-cleanup"
    HABIT = "habit"
    CHORE = "chore"
    BIG_PLAN = "big-plan"
    JOURNAL = "journal"
    METRIC = "metric"
    PERSON_CATCH_UP = "person-catch-up"
    PERSON_BIRTHDAY = "person-birthday"
    SLACK_TASK = "slack-task"
    EMAIL_TASK = "email-task"

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self in (
            InboxTaskSource.USER,
            InboxTaskSource.BIG_PLAN,
            InboxTaskSource.SLACK_TASK,
            InboxTaskSource.EMAIL_TASK,
        )
