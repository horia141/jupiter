"""A repository of inbox tasks."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class InboxTaskNotFoundError(LeafEntityNotFoundError):
    """Error raised when an inbox task does not exist."""


class InboxTaskRepository(LeafEntityRepository[InboxTask], abc.ABC):
    """A repository of inbox tasks."""

    @abc.abstractmethod
    async def find_all_with_filters(
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
        filter_last_modified_time_start: Optional[ADate] = None,
        filter_last_modified_time_end: Optional[ADate] = None,
    ) -> List[InboxTask]:
        """Find all inbox tasks."""
