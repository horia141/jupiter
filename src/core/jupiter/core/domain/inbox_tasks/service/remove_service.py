"""Shared service for removing an inbox task."""
from typing import Final

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.use_case import ProgressReporter


class InboxTaskRemoveService:
    """Shared service for removing an inbox task."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ProgressReporter,
        inbox_task: InboxTask,
    ) -> None:
        """Execute the service's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            await uow.inbox_task_repository.remove(inbox_task.ref_id)
            await progress_reporter.mark_removed(inbox_task)
