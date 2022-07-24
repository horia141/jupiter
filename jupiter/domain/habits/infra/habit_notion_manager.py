"""A manager of Notion-side habits."""
import abc
from typing import Iterable

from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionHabitNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion habit was not found."""


class HabitNotionManager(
    ParentTrunkLeafNotionManager[NotionWorkspace, NotionHabitCollection, NotionHabit]
):
    """A manager of Notion-side habits."""

    @abc.abstractmethod
    def upsert_habits_project_field_options(
        self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""
