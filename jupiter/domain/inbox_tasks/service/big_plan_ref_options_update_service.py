"""Service for updating the big plan references on Notion side to the current set of big plans."""
from typing import Final

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, InboxTaskBigPlanLabel
from jupiter.domain.storage_engine import DomainStorageEngine


class InboxTaskBigPlanRefOptionsUpdateService:
    """Service for updating the big plan references on Notion side to the current set of big plans."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def sync(self, big_plan_collection: BigPlanCollection) -> None:
        """Execute the service's actions."""
        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_project(big_plan_collection.project_ref_id)
            all_big_plans = \
                uow.big_plan_repository.find_all(
                    filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
        self._inbox_task_notion_manager.upsert_inbox_tasks_big_plan_field_options(
            inbox_task_collection.ref_id,
            (InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans))
