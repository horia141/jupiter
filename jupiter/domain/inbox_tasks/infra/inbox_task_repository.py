"""A repository of inbox tasks."""
import abc
from typing import Optional, Iterable, List

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class InboxTaskNotFoundError(LeafEntityNotFoundError):
    """Error raised when an inbox task does not exist."""


class InboxTaskRepository(LeafEntityRepository[InboxTask], abc.ABC):
    """A repository of inbox tasks."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_sources: Optional[Iterable[InboxTaskSource]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_habit_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_chore_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_person_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_slack_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_email_task_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[InboxTask]:
        """Find all inbox tasks."""
