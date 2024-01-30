"""A tag for all the known entities."""

from jupiter.core.framework.entity import CrownEntity
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
    def from_entity(entity: CrownEntity) -> "NamedEntityTag":
        """Construct a tag from an entity."""
        return NamedEntityTag(entity.__class__.__name__)
