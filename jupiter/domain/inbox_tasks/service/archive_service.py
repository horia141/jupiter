"""Shared service for archiving an inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.storage_engine import StorageEngine
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskArchiveService:
    """Shared service for archiving an inbox task."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, inbox_task: InboxTask) -> None:
        """Execute the service's action."""
        inbox_task.mark_archived(self._time_provider.get_current_time())

        with self._storage_engine.get_unit_of_work() as uow:
            uow.inbox_task_repository.save(inbox_task)
        LOGGER.info("Applied local changes")

        # Apply Notion changes
        try:
            self._inbox_task_notion_manager.remove_inbox_task(
                inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
        except NotionInboxTaskNotFoundError:
            LOGGER.info("Skipping archiving of Notion inbox task because it could not be found")