"""A manager of Notion-side big plans."""
import abc
from typing import Iterable

from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
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


class NotionBigPlanNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion big plan was not found."""


class BigPlanNotionManager(
    ParentTrunkLeafNotionManager[
        NotionWorkspace,
        NotionBigPlanCollection,
        NotionBigPlan,
        NotionInboxTaskCollection,
    ]
):
    """A manager of Notion-side big plans."""

    @abc.abstractmethod
    def upsert_big_plans_project_field_options(
        self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]
    ) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""
