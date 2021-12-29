"""Shared service for archiving a recurring task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager, \
    NotionRecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.storage_engine import StorageEngine
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskArchiveService:
    """Shared service for archiving a recurring task."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def do_it(self, recurring_task: RecurringTask) -> None:
        """Execute the service's action."""
        if recurring_task.archived:
            return

        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task.mark_archived(self._time_provider.get_current_time())
            uow.recurring_task_repository.save(recurring_task)

            recurring_task_collection = \
                uow.recurring_task_collection_repository.load_by_id(recurring_task.recurring_task_collection_ref_id)

            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_project(recurring_task_collection.project_ref_id)
            inbox_tasks_to_archive = uow.inbox_task_repository.find_all(
                allow_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id],
                filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                inbox_task.mark_archived(self._time_provider.get_current_time())
                uow.inbox_task_repository.save(inbox_task)

        try:
            self._recurring_task_notion_manager.remove_recurring_task(
                recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        except NotionRecurringTaskNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping archival on Notion side because recurring task was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping archival on Notion side because inbox task was not found")
