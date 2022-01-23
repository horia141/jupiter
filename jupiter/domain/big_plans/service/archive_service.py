"""Shared logic for archiving a big plan."""
import logging
from typing import Final

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager, NotionBigPlanNotFoundError
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class BigPlanArchiveService:
    """Shared logic for archiving a big plan."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, source: EventSource, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def do_it(self, big_plan: BigPlan) -> None:
        """Execute the service's action."""
        if big_plan.archived:
            return

        with self._storage_engine.get_unit_of_work() as uow:
            big_plan = big_plan.mark_archived(self._source, self._time_provider.get_current_time())
            uow.big_plan_repository.save(big_plan)

            big_plan_collection = uow.big_plan_collection_repository.load_by_id(big_plan.big_plan_collection_ref_id)

            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_project(big_plan_collection.project_ref_id)
            inbox_tasks_to_archive = \
                uow.inbox_task_repository.find_all(
                    allow_archived=False, filter_big_plan_ref_ids=[big_plan.ref_id],
                    filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])
            archived_inbox_tasks = []
            for inbox_task in inbox_tasks_to_archive:
                inbox_task = inbox_task.mark_archived(self._source, self._time_provider.get_current_time())
                uow.inbox_task_repository.save(inbox_task)
                archived_inbox_tasks.append(inbox_task)

        try:
            self._big_plan_notion_manager.remove_big_plan(big_plan.big_plan_collection_ref_id, big_plan.ref_id)
        except NotionBigPlanNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping archival on Notion side because big plan was not found")

        for inbox_task in archived_inbox_tasks:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping archival on Notion side because inbox task was not found")
