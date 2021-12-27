"""A manager of Notion-side inbox tasks."""
import abc
import uuid
from dataclasses import dataclass
from typing import Optional, Iterable

from domain.entity_name import EntityName
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from domain.projects.notion_project import NotionProject
from framework.base.entity_id import EntityId
from framework.base.notion_id import NotionId


class NotionInboxTaskCollectionNotFoundError(Exception):
    """Exception raised when a Notion inbox task collection was not found."""


class NotionInboxTaskNotFoundError(Exception):
    """Exception raised when a Notion inbox task was not found."""


@dataclass(frozen=True)
class InboxTaskBigPlanLabel:
    """A value for an inbox task big plan label."""
    notion_link_uuid: uuid.UUID
    name: EntityName


class InboxTaskNotionManager(abc.ABC):
    """A manager of Notion-side inbox tasks."""

    @abc.abstractmethod
    def upsert_inbox_task_collection(
            self, notion_project: NotionProject,
            inbox_task_collection: NotionInboxTaskCollection) -> NotionInboxTaskCollection:
        """Upsert the Notion-side inbox task."""

    @abc.abstractmethod
    def load_inbox_task_collection(self, ref_id: EntityId) -> NotionInboxTaskCollection:
        """Retrieve the Notion-side inbox task collection."""

    @abc.abstractmethod
    def remove_inbox_tasks_collection(self, ref_id: EntityId) -> None:
        """Remove the Notion-side structure for this collection."""

    @abc.abstractmethod
    def upsert_inbox_tasks_big_plan_field_options(
            self, ref_id: EntityId, big_plans_labels: Iterable[InboxTaskBigPlanLabel]) -> None:
        """Upsert the Notion-side structure for the 'big plan' select field."""

    @abc.abstractmethod
    def upsert_inbox_task(
            self, inbox_task_collection_ref_id: EntityId, inbox_task: NotionInboxTask) -> NotionInboxTask:
        """Upsert a inbox task."""

    @abc.abstractmethod
    def save_inbox_task(self, inbox_task_collection_ref_id: EntityId, inbox_task: NotionInboxTask) -> NotionInboxTask:
        """Update the Notion-side inbox task with new data."""

    @abc.abstractmethod
    def load_all_inbox_tasks(self, inbox_task_collection_ref_id: EntityId) -> Iterable[NotionInboxTask]:
        """Retrieve all the Notion-side inbox tasks."""

    @abc.abstractmethod
    def load_inbox_task(self, inbox_task_collection_ref_id: EntityId, ref_id: EntityId) -> NotionInboxTask:
        """Retrieve the Notion-side inbox task associated with a particular entity."""

    @abc.abstractmethod
    def remove_inbox_task(self, inbox_task_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""

    @abc.abstractmethod
    def drop_all_inbox_tasks(self, inbox_task_collection_ref_id: EntityId) -> None:
        """Remove all inbox tasks Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_inbox_task(
            self, inbox_task_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_inbox_tasks_notion_ids(self, inbox_task_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""

    @abc.abstractmethod
    def load_all_saved_inbox_tasks_ref_ids(self, inbox_task_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the inbox tasks tasks."""
