"""A manager of Notion-side chores."""
import abc
from typing import Iterable

from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.notion_manager import (
    ParentTrunkLeafNotionManager,
    NotionLeafEntityNotFoundError,
)


class NotionChoreNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion chore was not found."""


class ChoreNotionManager(
    ParentTrunkLeafNotionManager[NotionWorkspace, NotionChoreCollection, NotionChore]
):
    """A manager of Notion-side chores."""

    @abc.abstractmethod
    def upsert_chores_project_field_options(
        self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""
