"""Shared service for archiving an inbox task."""
from typing import Final

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class InboxTaskArchiveService:
    """Shared service for archiving an inbox task."""

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
        self,
        progress_reporter: ContextProgressReporter,
        inbox_task: InboxTask,
    ) -> None:
        """Execute the service's action."""
        if inbox_task.archived:
            return

        async with progress_reporter.start_archiving_entity(
            "inbox task",
            inbox_task.ref_id,
            str(inbox_task.name),
        ) as entity_reporter:
            inbox_task = inbox_task.mark_archived(
                self._source,
                self._time_provider.get_current_time(),
            )

            async with self._storage_engine.get_unit_of_work() as uow:
                await uow.inbox_task_repository.save(inbox_task)
            await entity_reporter.mark_local_change()
