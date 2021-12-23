"""A repository of recurring tasks."""
import abc
from typing import Optional, Iterable

from domain.recurring_tasks.recurring_task import RecurringTask
from domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from framework.base.entity_id import EntityId
from framework.storage import Repository


class RecurringTaskRepository(Repository, abc.ABC):
    """A repository of recurring tasks."""

    @abc.abstractmethod
    def create(
            self, recurring_task_collection: RecurringTaskCollection, recurring_task: RecurringTask) -> RecurringTask:
        """Create a recurring task."""

    @abc.abstractmethod
    def save(self, recurring_task: RecurringTask) -> RecurringTask:
        """Save a recurring task - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTask:
        """Load a recurring task by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_collection_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Find all recurring tasks."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> RecurringTask:
        """Hard remove a recurring task - an irreversible operation."""
