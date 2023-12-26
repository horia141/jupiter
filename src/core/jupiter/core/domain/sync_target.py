"""What exactly to sync."""
from functools import lru_cache
from typing import Iterable, Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class SyncTarget(EnumValue):
    """What exactly to generate, gc, or look at systematically."""

    INBOX_TASKS = "inbox-tasks"
    HABITS = "habits"
    CHORES = "chores"
    BIG_PLANS = "big-plans"
    DOCS = "docs"
    VACATIONS = "vacations"
    PROJECTS = "projects"
    SMART_LISTS = "smart-lists"
    METRICS = "metrics"
    PERSONS = "persons"
    SLACK_TASKS = "slack-tasks"
    EMAIL_TASKS = "email-tasks"

    @staticmethod
    def from_raw(sync_target_raw: Optional[str]) -> "SyncTarget":
        """Validate and clean the synt target."""
        if not sync_target_raw:
            raise InputValidationError("Expected sync target to be non-null")

        sync_target_str: str = sync_target_raw.strip().lower()

        if sync_target_str not in SyncTarget.all_values():
            raise InputValidationError(
                f"Expected sync prefer '{sync_target_raw}' to be one of '{','.join(SyncTarget.all_values())}'",
            )

        return SyncTarget(sync_target_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in SyncTarget)
