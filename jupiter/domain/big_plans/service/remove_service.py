"""Shared module for removing a big plan."""
import logging
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager, \
    NotionBigPlanNotFoundError
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class BigPlanRemoveService:
    """Shared service for removing a big plan."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an big plan."""
        with self._storage_engine.get_unit_of_work() as uow:
            big_plan = uow.big_plan_repository.remove(ref_id)
            big_plan_collection = uow.big_plan_collection_repository.load_by_id(big_plan.big_plan_collection_ref_id)

            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_workspace(big_plan_collection.workspace_ref_id)
            inbox_tasks_to_remove = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_big_plan_ref_ids=[big_plan.ref_id])
            for inbox_task in inbox_tasks_to_remove:
                uow.inbox_task_repository.remove(inbox_task.ref_id)

        try:
            self._big_plan_notion_manager.remove_big_plan(big_plan.big_plan_collection_ref_id, big_plan.ref_id)
        except NotionBigPlanNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because big plan was not found")

        for inbox_task in inbox_tasks_to_remove:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")
