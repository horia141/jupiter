"""The command for archiving a recurring task."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.service.archive_service import RecurringTaskArchiveService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskArchiveUseCase(AppMutationUseCase['RecurringTaskArchiveUseCase.Args', None]):
    """The command for archiving a recurring task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)
        RecurringTaskArchiveService(
            EventSource.CLI, self._time_provider, self._storage_engine, self._inbox_task_notion_manager,
            self._recurring_task_notion_manager).do_it(recurring_task)
