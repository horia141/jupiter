"""Shared module for removing a big plan."""
import logging
from typing import Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager, NotionBigPlanNotFoundError
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, NotionInboxTaskNotFoundError
from framework.base.entity_id import EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanRemoveService:
    """Shared service for removing a big plan."""

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, big_plan_engine: BigPlanEngine,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an big plan."""
        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan = big_plan_uow.big_plan_repository.remove(ref_id)

        try:
            self._big_plan_notion_manager.remove_big_plan(big_plan.project_ref_id, big_plan.ref_id)
        except NotionBigPlanNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because big plan was not found")

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = \
                inbox_task_uow.inbox_task_collection_repository.load_by_project(big_plan.project_ref_id)
            inbox_tasks_to_archive = \
                inbox_task_uow.inbox_task_repository.find_all(
                    allow_archived=False, filter_big_plan_ref_ids=[big_plan.ref_id],
                    filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                inbox_task_uow.inbox_task_repository.remove(inbox_task.ref_id)

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(inbox_task.project_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")
