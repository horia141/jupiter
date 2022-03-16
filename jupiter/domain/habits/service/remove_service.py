"""Shared service for removing a habit."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager, \
    NotionHabitNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class HabitRemoveService:
    """Shared service for removing a habit."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an habit."""
        with self._storage_engine.get_unit_of_work() as uow:
            habit = uow.habit_repository.remove(ref_id)

            habit_collection = \
                uow.habit_collection_repository.load_by_id(habit.habit_collection_ref_id)

            inbox_task_collection = \
                uow.inbox_task_collection_repository.load_by_parent(habit_collection.workspace_ref_id)
            inbox_tasks_to_archive = \
                uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_habit_ref_ids=[habit.ref_id])
            for inbox_task in inbox_tasks_to_archive:
                uow.inbox_task_repository.remove(inbox_task.ref_id)

        try:
            self._habit_notion_manager.remove_leaf(habit.habit_collection_ref_id, habit.ref_id)
        except NotionHabitNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because habit was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_leaf(inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")
