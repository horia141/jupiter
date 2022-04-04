"""Shared service for archiving a chore."""
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
from jupiter.domain.chores.chore import Chore
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ChoreArchiveService:
    """Shared service for archiving a chore."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        chore_notion_manager: ChoreNotionManager,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._chore_notion_manager = chore_notion_manager

    def do_it(self, chore: Chore) -> None:
        """Execute the service's action."""
        if chore.archived:
            return

        with self._storage_engine.get_unit_of_work() as uow:
            chore = chore.mark_archived(
                self._source, self._time_provider.get_current_time()
            )
            uow.chore_repository.save(chore)

            chore_collection = uow.chore_collection_repository.load_by_id(
                chore.chore_collection_ref_id
            )

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                chore_collection.workspace_ref_id
            )
            inbox_tasks_to_archive = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_chore_ref_ids=[chore.ref_id],
            )
            for inbox_task in inbox_tasks_to_archive:
                inbox_task = inbox_task.mark_archived(
                    self._source, self._time_provider.get_current_time()
                )
                uow.inbox_task_repository.save(inbox_task)

        try:
            self._chore_notion_manager.remove_leaf(
                chore.chore_collection_ref_id, chore.ref_id
            )
        except NotionChoreNotFoundError:
            # If we can't find this locally it means it's already gone
            LOGGER.info("Skipping archival on Notion side because chore was not found")

        for inbox_task in inbox_tasks_to_archive:
            try:
                self._inbox_task_notion_manager.remove_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping archival on Notion side because inbox task was not found"
                )
