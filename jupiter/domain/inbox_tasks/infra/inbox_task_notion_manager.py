"""A manager of Notion-side inbox tasks."""
import abc
from typing import Iterable

from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import (
    NotionInboxTaskCollection,
)
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionInboxTaskCollectionNotFoundError(Exception):
    """Exception raised when a Notion inbox task collection was not found."""


class NotionInboxTaskNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion inbox task was not found."""


class InboxTaskNotionManager(
    ParentTrunkLeafNotionManager[
        NotionWorkspace, NotionInboxTaskCollection, NotionInboxTask, None
    ]
):
    """A manager of Notion-side inbox tasks."""

    @abc.abstractmethod
    def load_trunk(self, ref_id: EntityId) -> NotionInboxTaskCollection:
        """Retrieve the Notion-side inbox task collection."""

    @abc.abstractmethod
    def upsert_inbox_tasks_project_field_options(
        self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""

    @abc.abstractmethod
    def upsert_inbox_tasks_big_plan_field_options(
        self, ref_id: EntityId, big_plans_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'big plan' select field."""
