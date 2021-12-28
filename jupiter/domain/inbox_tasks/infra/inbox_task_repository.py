"""A repository of inbox tasks."""
import abc
from typing import Optional, Iterable

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class InboxTaskNotFoundError(Exception):
    """Error raised when an inbox task does not exist."""


class InboxTaskRepository(Repository, abc.ABC):
    """A repository of inbox tasks."""

    @abc.abstractmethod
    def create(self, inbox_task_collection: InboxTaskCollection, inbox_task: InboxTask) -> InboxTask:
        """Create a inbox task."""

    @abc.abstractmethod
    def save(self, inbox_task: InboxTask) -> InboxTask:
        """Save a inbox task - it should already exist."""

    @abc.abstractmethod
    def dump_all(self, inbox_tasks: Iterable[InboxTask]) -> None:
        """Save all inbox tasks - good for migrations."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTask:
        """Load a inbox task by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_inbox_task_collection_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_sources: Optional[Iterable[InboxTaskSource]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_person_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Find all inbox tasks."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> InboxTask:
        """Hard remove a inbox task - an irreversible operation."""
