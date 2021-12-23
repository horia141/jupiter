"""Shared service for removing a recurring task."""
import logging
from typing import Final

import remote
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from framework.base.entity_id import EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskRemoveService:
    """Shared service for removing a recurring task."""
    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, recurring_task_engine: RecurringTaskEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an recurring task."""
        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            recurring_task = recurring_task_uow.recurring_task_repository.remove(ref_id)

        try:
            self._recurring_task_notion_manager.remove_recurring_task(
                recurring_task.project_ref_id, recurring_task.ref_id)
        except remote.notion.common.CollectionEntityNotFound:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because recurring task was not found")

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = \
                inbox_task_uow.inbox_task_collection_repository.load_by_project(recurring_task.project_ref_id)
            inbox_tasks_to_archive = \
                inbox_task_uow.inbox_task_repository.find_all(
                    allow_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id],
                    filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                inbox_task_uow.inbox_task_repository.remove(inbox_task.ref_id)

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_inbox_task(inbox_task.project_ref_id, inbox_task.ref_id)
            except remote.notion.common.CollectionEntityNotFound:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")
