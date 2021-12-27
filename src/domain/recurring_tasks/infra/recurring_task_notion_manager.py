"""A manager of Notion-side recurring tasks."""
import abc
from typing import Optional, Iterable

from domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from domain.projects.notion_project import NotionProject
from domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from domain.recurring_tasks.notion_recurring_task_collection import NotionRecurringTaskCollection
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId


class NotionRecurringTaskCollectionNotFoundError(Exception):
    """Exception raised when a Notion recurring task collection was not found."""


class NotionRecurringTaskNotFoundError(Exception):
    """Exception raised when a Notion recurring task was not found."""


class RecurringTaskNotionManager(abc.ABC):
    """A manager of Notion-side recurring tasks."""

    @abc.abstractmethod
    def upsert_recurring_task_collection(
            self, notion_project: NotionProject,
            recurring_task_collection: NotionRecurringTaskCollection) -> NotionRecurringTaskCollection:
        """Upsert the Notion-side recurring task."""

    @abc.abstractmethod
    def load_recurring_task_collection(self, ref_id: EntityId) -> NotionRecurringTaskCollection:
        """Retrieve the Notion-side recurring task collection."""

    @abc.abstractmethod
    def remove_recurring_tasks_collection(self, ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""

    @abc.abstractmethod
    def upsert_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, recurring_task: NotionRecurringTask,
            inbox_collection_link: NotionInboxTaskCollection) -> NotionRecurringTask:
        """Upsert a recurring task."""

    @abc.abstractmethod
    def save_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, recurring_task: NotionRecurringTask,
            inbox_collection_link: Optional[NotionInboxTaskCollection] = None) -> NotionRecurringTask:
        """Update the Notion-side recurring task with new data."""

    @abc.abstractmethod
    def load_recurring_task(self, recurring_task_collection_ref_id: EntityId, ref_id: EntityId) -> NotionRecurringTask:
        """Retrieve the Notion-side recurring task associated with a particular entity."""

    @abc.abstractmethod
    def load_all_recurring_tasks(
            self, recurring_task_collection_ref_id: EntityId) -> Iterable[NotionRecurringTask]:
        """Retrieve all the Notion-side recurring tasks."""

    @abc.abstractmethod
    def remove_recurring_task(self, recurring_task_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""

    @abc.abstractmethod
    def drop_all_recurring_tasks(self, recurring_task_collection_ref_id: EntityId) -> None:
        """Remove all recurring tasks Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_recurring_task(
            self, recurring_task_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_recurring_tasks_notion_ids(
            self, recurring_task_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""

    @abc.abstractmethod
    def load_all_saved_recurring_tasks_ref_ids(self, recurring_task_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the recurring tasks tasks."""
