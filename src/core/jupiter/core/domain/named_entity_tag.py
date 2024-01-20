"""A tag for all the known entities."""
from functools import lru_cache
from typing import Iterable, Optional

from jupiter.core.framework.entity import CrownEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class NamedEntityTag(EnumValue):
    """A tag for all known entities."""

    INBOX_TASK = "InboxTask"  # InboxTask.__name__
    HABIT = "Habit"  # Habit.__name__
    CHORE = "Chore"  # Chore.__name__
    BIG_PLAN = "BigPlan"  # BigPlan.__name__
    DOC = "Doc"  # Doc.__name__
    JOURNAL = "Journal"  # Journal.__name__
    VACATION = "Vacation"  # Vacation.__name__
    PROJECT = "Project"  # Project.__name__
    SMART_LIST = "SmartList"  # SmartList.__name__
    SMART_LIST_TAG = "SmartListTag"  # SmartListTag.__name__
    SMART_LIST_ITEM = "SmartListItem"  # SmartListItem.__name__
    METRIC = "Metric"  # Metric.__name__
    METRIC_ENTRY = "MetricEntry"  # MetricEntry.__name__
    PERSON = "Person"  # Person.__name__
    SLACK_TASK = "SlackTask"  # SlackTask.__name__
    EMAIL_TASK = "EmailTask"  # EmailTask.__name__

    @staticmethod
    def from_raw(named_entity_tag_raw: Optional[str]) -> "NamedEntityTag":
        """Validate and clean the entity tag."""
        if not named_entity_tag_raw:
            raise InputValidationError("Expected entity tag to be non-null")

        named_entity_tag_str: str = named_entity_tag_raw.strip()

        if named_entity_tag_str not in NamedEntityTag.all_values():
            raise InputValidationError(
                f"Expected entity tag '{named_entity_tag_raw}' to be one of '{','.join(NamedEntityTag.all_values())}' but was {named_entity_tag_str}",
            )

        return NamedEntityTag(named_entity_tag_str)

    @staticmethod
    def from_entity(entity: CrownEntity) -> "NamedEntityTag":
        """Construct a tag from an entity."""
        return NamedEntityTag(entity.__class__.__name__)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in NamedEntityTag)

    def __str__(self) -> str:
        """The string value."""
        return str(self.value)
