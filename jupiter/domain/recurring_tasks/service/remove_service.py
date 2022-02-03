"""Shared service for removing a recurring task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager, \
    NotionRecurringTaskNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class RecurringTaskRemoveService:
    """Shared service for removing a recurring task."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an recurring task."""
        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.remove(ref_id)

            recurring_task_collection = \
                uow.recurring_task_collection_repository.load_by_id(recurring_task.recurring_task_collection_ref_id)

            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_workspace(recurring_task_collection.workspace_ref_id)
            inbox_tasks_to_archive = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                uow.inbox_task_repository.remove(inbox_task.ref_id)

        try:
            self._recurring_task_notion_manager.remove_recurring_task(
                recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        except NotionRecurringTaskNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because recurring task was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")
