"""Shared service for archiving a chore."""
import logging
from typing import Final

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter
from jupiter.core.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ChoreArchiveService:
    """Shared service for archiving a chore."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    async def do_it(
        self, progress_reporter: ContextProgressReporter, chore: Chore
    ) -> None:
        """Execute the service's action."""
        if chore.archived:
            return

        async with self._storage_engine.get_unit_of_work() as uow:
            chore_collection = await uow.chore_collection_repository.load_by_id(
                chore.chore_collection_ref_id,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    chore_collection.workspace_ref_id,
                )
            )
            inbox_tasks_to_archive = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=False,
                    filter_chore_ref_ids=[chore.ref_id],
                )
            )

        for inbox_task in inbox_tasks_to_archive:
            async with progress_reporter.start_archiving_entity(
                "inbox task",
                inbox_task.ref_id,
                str(inbox_task.name),
            ) as entity_reporter:
                async with self._storage_engine.get_unit_of_work() as uow:
                    inbox_task = inbox_task.mark_archived(
                        self._source,
                        self._time_provider.get_current_time(),
                    )
                    await uow.inbox_task_repository.save(inbox_task)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.start_archiving_entity(
            "chore",
            chore.ref_id,
            str(chore.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                chore = chore.mark_archived(
                    self._source,
                    self._time_provider.get_current_time(),
                )
                await uow.chore_repository.save(chore)
                await entity_reporter.mark_local_change()
