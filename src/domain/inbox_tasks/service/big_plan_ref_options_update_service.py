"""Service for updating the big plan references on Notion side to the current set of big plans."""
from typing import Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.inbox_task_big_plan_label import InboxTaskBigPlanLabel
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.projects.project import Project


class InboxTaskBigPlanRefOptionsUpdateService:
    """Service for updating the big plan references on Notion side to the current set of big plans."""

    _big_plan_engine: Final[BigPlanEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(self, big_plan_engine: BigPlanEngine, inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._big_plan_engine = big_plan_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def sync(self, project: Project) -> None:
        """Execute the service's actions."""
        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan_collection = big_plan_uow.big_plan_collection_repository.load_by_project(project.ref_id)
            all_big_plans = \
                big_plan_uow.big_plan_repository.find_all(
                    filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
        self._inbox_task_notion_manager.upsert_inbox_tasks_big_plan_field_options(
            project.ref_id,
            (InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans))
