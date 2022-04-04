"""Shared service for removing a chore."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
    NotionInboxTaskNotFoundError,
)
from jupiter.domain.chores.infra.chore_notion_manager import (
    ChoreNotionManager,
    NotionChoreNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class ChoreRemoveService:
    """Shared service for removing a chore."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        chore_notion_manager: ChoreNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._chore_notion_manager = chore_notion_manager

    def remove(self, ref_id: EntityId) -> None:
        """Hard remove an chore."""
        with self._storage_engine.get_unit_of_work() as uow:
            chore = uow.chore_repository.remove(ref_id)

            chore_collection = uow.chore_collection_repository.load_by_id(
                chore.chore_collection_ref_id
            )

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                chore_collection.workspace_ref_id
            )
            inbox_tasks_to_archive = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_chore_ref_ids=[chore.ref_id],
            )
            for inbox_task in inbox_tasks_to_archive:
                uow.inbox_task_repository.remove(inbox_task.ref_id)

        try:
            self._chore_notion_manager.remove_leaf(
                chore.chore_collection_ref_id, chore.ref_id
            )
        except NotionChoreNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping removal on Notion side because chore was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because inbox task was not found"
                )
