"""Shared service for removing an inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
    NotionInboxTaskNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

LOGGER = logging.getLogger(__name__)


class InboxTaskRemoveService:
    """Shared service for removing an inbox task."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, progress_reporter: ProgressReporter, inbox_task: InboxTask) -> None:
        """Execute the service's action."""
        with progress_reporter.start_removing_entity(
            "inbox task", inbox_task.ref_id, str(inbox_task.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                uow.inbox_task_repository.remove(inbox_task.ref_id)
                entity_reporter.mark_local_change()

            try:
                self._inbox_task_notion_manager.remove_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                entity_reporter.mark_local_change()
            except NotionInboxTaskNotFoundError:
                LOGGER.info(
                    "Skipping archiving of Notion inbox task because it could not be found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
