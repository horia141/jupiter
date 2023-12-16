"""A tag for all the known entities."""
import enum
from functools import lru_cache
from typing import Iterable, Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.errors import InputValidationError


@enum.unique
class NamedEntityTag(enum.Enum):
    """A tag for all known entities."""

    INBOX_TASK = InboxTask.__name__
    HABIT = Habit.__name__
    CHORE = Chore.__name__
    BIG_PLAN = BigPlan.__name__
    DOC = Doc.__name__
    VACATION = Vacation.__name__
    PROJECT = Project.__name__
    SMART_LIST = SmartList.__name__
    SMART_LIST_TAG = SmartListTag.__name__
    SMART_LIST_ITEM = SmartListItem.__name__
    METRIC = Metric.__name__
    METRIC_ENTRY = MetricEntry.__name__
    PERSON = Person.__name__
    SLACK_TASK = SlackTask.__name__
    EMAIL_TASK = EmailTask.__name__

    @staticmethod
    def from_raw(named_entity_tag_raw: Optional[str]) -> "NamedEntityTag":
        """Validate and clean the entity tag."""
        if not named_entity_tag_raw:
            raise InputValidationError("Expected entity tag to be non-null")

        named_entity_tag_str: str = named_entity_tag_raw.strip()

        if named_entity_tag_str not in NamedEntityTag.all_values():
            raise InputValidationError(
                f"Expected entity tag '{named_entity_tag_raw}' to be one of '{','.join(NamedEntityTag.all_values())}'",
            )

        return NamedEntityTag(named_entity_tag_str)

    @staticmethod
    def from_entity(entity: BranchEntity | LeafEntity) -> "NamedEntityTag":
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
