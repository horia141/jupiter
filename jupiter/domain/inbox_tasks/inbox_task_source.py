"""The origin of an inbox task."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from jupiter.framework.errors import InputValidationError


@enum.unique
class InboxTaskSource(enum.Enum):
    """The origin of an inbox task."""

    USER = "user"
    BIG_PLAN = "big-plan"
    HABIT = "habit"
    CHORE = "chore"
    METRIC = "metric"
    PERSON_CATCH_UP = "person-catch-up"
    PERSON_BIRTHDAY = "person-birthday"
    SLACK_TASK = "slack-task"
    EMAIL_TASK = "email-task"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self in (
            InboxTaskSource.USER,
            InboxTaskSource.BIG_PLAN,
            InboxTaskSource.SLACK_TASK,
            InboxTaskSource.EMAIL_TASK,
        )

    @staticmethod
    def from_raw(inbox_task_source_raw: Optional[str]) -> "InboxTaskSource":
        """Validate and clean the big plan source."""
        if not inbox_task_source_raw:
            raise InputValidationError("Expected inbox task source to be non-null")

        inbox_task_source_str: str = "-".join(
            inbox_task_source_raw.strip().lower().split(" ")
        )

        if inbox_task_source_str not in InboxTaskSource.all_values():
            raise InputValidationError(
                f"Expected inbox task source '{inbox_task_source_raw}' to be "
                + f"one of '{','.join(InboxTaskSource.all_values())}'"
            )

        return InboxTaskSource(inbox_task_source_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in InboxTaskSource)

    def __str__(self) -> str:
        """String form."""
        return str(self.value)
