"""A manager of Notion-side big plans."""
import abc
from typing import Optional, Iterable

from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId

class NotionBigPlanNotFoundError(Exception):
    """Exception raised when a Notion big plan was not found."""


class BigPlanNotionManager(abc.ABC):
    """A manager of Notion-side big plans."""

    @abc.abstractmethod
    def upsert_big_plan_collection(
            self, notion_workspace: NotionWorkspace,
            big_plan_collection: NotionBigPlanCollection) -> NotionBigPlanCollection:
        """Upsert the Notion-side big plan."""

    @abc.abstractmethod
    def upsert_big_plans_project_field_options(
            self, ref_id: EntityId, project_labels: Iterable[NotionFieldLabel]) -> None:
        """Upsert the Notion-side structure for the 'project' select field."""

    @abc.abstractmethod
    def upsert_big_plan(
            self, big_plan_collection_ref_id: EntityId, big_plan: NotionBigPlan,
            inbox_collection_link: NotionInboxTaskCollection) -> NotionBigPlan:
        """Upsert a big plan."""

    @abc.abstractmethod
    def save_big_plan(
            self, big_plan_collection_ref_id: EntityId, big_plan: NotionBigPlan,
            inbox_collection_link: Optional[NotionInboxTaskCollection] = None) -> NotionBigPlan:
        """Update the Notion-side big plan with new data."""

    @abc.abstractmethod
    def load_big_plan(self, big_plan_collection_ref_id: EntityId, ref_id: EntityId) -> NotionBigPlan:
        """Retrieve the Notion-side big plan associated with a particular entity."""

    @abc.abstractmethod
    def load_all_big_plans(self, big_plan_collection_ref_id: EntityId) -> Iterable[NotionBigPlan]:
        """Retrieve all the Notion-side big plans."""

    @abc.abstractmethod
    def remove_big_plan(self, big_plan_collection_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""

    @abc.abstractmethod
    def drop_all_big_plans(self, big_plan_collection_ref_id: EntityId) -> None:
        """Remove all big plans Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_big_plan(
            self, big_plan_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_big_plans_notion_ids(self, big_plan_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these tasks."""

    @abc.abstractmethod
    def load_all_saved_big_plans_ref_ids(self, big_plan_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the big plans tasks."""
