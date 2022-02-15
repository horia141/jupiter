"""A manager of Notion-side habits."""
import abc
from typing import Optional, Iterable

from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionHabitNotFoundError(Exception):
    """Exception raised when a Notion habit was not found."""


class HabitNotionManager(abc.ABC):
    """A manager of Notion-side habits."""

    @abc.abstractmethod
    def upsert_habit_collection(
            self, notion_workspace: NotionWorkspace,
            habit_collection: NotionHabitCollection) -> NotionHabitCollection:
        """Upsert the Notion-side habit."""

    @abc.abstractmethod
    def upsert_habits_project_field_options(
            self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""

    @abc.abstractmethod
    def upsert_habit(
            self, habit_collection_ref_id: EntityId, habit: NotionHabit,
            inbox_collection_link: NotionInboxTaskCollection) -> NotionHabit:
        """Upsert a habit."""

    @abc.abstractmethod
    def save_habit(
            self, habit_collection_ref_id: EntityId, habit: NotionHabit,
            inbox_collection_link: Optional[NotionInboxTaskCollection] = None) -> NotionHabit:
        """Update the Notion-side habit with new data."""

    @abc.abstractmethod
    def load_habit(self, habit_collection_ref_id: EntityId, ref_id: EntityId) -> NotionHabit:
        """Retrieve the Notion-side habit associated with a particular entity."""

    @abc.abstractmethod
    def load_all_habits(
            self, habit_collection_ref_id: EntityId) -> Iterable[NotionHabit]:
        """Retrieve all the Notion-side habits."""

    @abc.abstractmethod
    def remove_habit(self, habit_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""

    @abc.abstractmethod
    def drop_all_habits(self, habit_collection_ref_id: EntityId) -> None:
        """Remove all habits Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_habit(
            self, habit_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_habits_notion_ids(
            self, habit_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""

    @abc.abstractmethod
    def load_all_saved_habits_ref_ids(self, habit_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the habits tasks."""
