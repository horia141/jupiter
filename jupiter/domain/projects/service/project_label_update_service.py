"""A service for updating project labels."""
from typing import Final, Iterable

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.project import Project
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.workspace import Workspace


class ProjectLabelUpdateService:
    """A service for updating project labels."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def sync(self, workspace: Workspace, projects: Iterable[Project]) -> None:
        """Execute the service's actions."""
        project_labels = [NotionFieldLabel(p.notion_link_uuid, p.name, p.created_time) for p in projects]

        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            recurring_task_collection = uow.recurring_task_collection_repository.load_by_workspace(workspace.ref_id)
            big_plan_collection = uow.big_plan_collection_repository.load_by_workspace(workspace.ref_id)

        self._inbox_task_notion_manager.upsert_inbox_tasks_project_field_options(
            inbox_task_collection.ref_id, project_labels)
        self._recurring_task_notion_manager.upsert_recurring_tasks_project_field_options(
            recurring_task_collection.ref_id, project_labels)
        self._big_plan_notion_manager.upsert_big_plans_project_field_options(
            big_plan_collection.ref_id, project_labels)
