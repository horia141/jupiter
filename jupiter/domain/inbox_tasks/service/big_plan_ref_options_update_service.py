"""Service for updating the big plan references on Notion side to the current set of big plans."""
from typing import Final

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.infra.big_plan_engine import BigPlanEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, InboxTaskBigPlanLabel


class InboxTaskBigPlanRefOptionsUpdateService:
    """Service for updating the big plan references on Notion side to the current set of big plans."""

    _big_plan_engine: Final[BigPlanEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, big_plan_engine: BigPlanEngine, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._big_plan_engine = big_plan_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def sync(self, big_plan_collection: BigPlanCollection) -> None:
        """Execute the service's actions."""
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = \
                inbox_task_uow.inbox_task_collection_repository.load_by_project(big_plan_collection.project_ref_id)
        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            all_big_plans = \
                big_plan_uow.big_plan_repository.find_all(
                    filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
        self._inbox_task_notion_manager.upsert_inbox_tasks_big_plan_field_options(
            inbox_task_collection.ref_id,
            (InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans))
