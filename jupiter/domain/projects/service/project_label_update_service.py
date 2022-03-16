"""A service for updating project labels."""
from typing import Final, Iterable

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.project import Project
from jupiter.domain.remote.notion.field_label import NotionFieldLabel
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.workspace import Workspace


class ProjectLabelUpdateService:
    """A service for updating project labels."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager,
            chore_notion_manager: ChoreNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager
        self._chore_notion_manager = chore_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def sync(self, workspace: Workspace, projects: Iterable[Project]) -> None:
        """Execute the service's actions."""
        project_labels = [NotionFieldLabel(p.notion_link_uuid, p.name, p.created_time) for p in projects]

        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(workspace.ref_id)
            habit_collection = uow.habit_collection_repository.load_by_parent(workspace.ref_id)
            chore_collection = uow.chore_collection_repository.load_by_parent(workspace.ref_id)
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(workspace.ref_id)

        self._inbox_task_notion_manager.upsert_inbox_tasks_project_field_options(
            inbox_task_collection.ref_id, project_labels)
        self._habit_notion_manager.upsert_habits_project_field_options(habit_collection.ref_id, project_labels)
        self._chore_notion_manager.upsert_chores_project_field_options(chore_collection.ref_id, project_labels)
        self._big_plan_notion_manager.upsert_big_plans_project_field_options(big_plan_collection.ref_id, project_labels)
