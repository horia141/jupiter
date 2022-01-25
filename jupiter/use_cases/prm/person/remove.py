"""Remove a person."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.prm.service.remove_service import PersonRemoveService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, MutationUseCaseInvocationRecorder
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonRemoveUseCase(AppMutationUseCase['PersonRemoveUseCase.Args', None]):
    """The command for removing a person."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_notion_manager = prm_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            person = uow.person_repository.load_by_id(args.ref_id)

        PersonRemoveService(self._storage_engine, self._prm_notion_manager, self._inbox_task_notion_manager)\
            .do_it(person)
