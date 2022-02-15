"""A manager of Notion-side chores."""
import abc
from typing import Optional, Iterable

from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionChoreNotFoundError(Exception):
    """Exception raised when a Notion chore was not found."""


class ChoreNotionManager(abc.ABC):
    """A manager of Notion-side chores."""

    @abc.abstractmethod
    def upsert_chore_collection(
            self, notion_workspace: NotionWorkspace,
            chore_collection: NotionChoreCollection) -> NotionChoreCollection:
        """Upsert the Notion-side chore."""

    @abc.abstractmethod
    def upsert_chores_project_field_options(
            self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""

    @abc.abstractmethod
    def upsert_chore(
            self, chore_collection_ref_id: EntityId, chore: NotionChore,
            inbox_collection_link: NotionInboxTaskCollection) -> NotionChore:
        """Upsert a chore."""

    @abc.abstractmethod
    def save_chore(
            self, chore_collection_ref_id: EntityId, chore: NotionChore,
            inbox_collection_link: Optional[NotionInboxTaskCollection] = None) -> NotionChore:
        """Update the Notion-side chore with new data."""

    @abc.abstractmethod
    def load_chore(self, chore_collection_ref_id: EntityId, ref_id: EntityId) -> NotionChore:
        """Retrieve the Notion-side chore associated with a particular entity."""

    @abc.abstractmethod
    def load_all_chores(
            self, chore_collection_ref_id: EntityId) -> Iterable[NotionChore]:
        """Retrieve all the Notion-side chores."""

    @abc.abstractmethod
    def remove_chore(self, chore_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""

    @abc.abstractmethod
    def drop_all_chores(self, chore_collection_ref_id: EntityId) -> None:
        """Remove all chores Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_chore(
            self, chore_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_chores_notion_ids(
            self, chore_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""

    @abc.abstractmethod
    def load_all_saved_chores_ref_ids(self, chore_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the chores tasks."""
