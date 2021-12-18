"""Shared service for removing an inbox task."""
import logging
from typing import Final

import remote
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskRemoveService:
    """Shared service for removing an inbox task."""

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, inbox_task: InboxTask) -> None:
        """Execute the service's action."""
        with self._inbox_task_engine.get_unit_of_work() as uow:
            uow.inbox_task_repository.remove(inbox_task.ref_id)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        try:
            self._inbox_task_notion_manager.remove_inbox_task(inbox_task.project_ref_id, inbox_task.ref_id)
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info("Skipping archiving of Notion inbox task because it could not be found")
