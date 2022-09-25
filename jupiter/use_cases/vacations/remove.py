"""The command for removing a vacation entry."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import (
    VacationNotionManager,
)
from jupiter.domain.vacations.service.remove_service import VacationRemoveService
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class VacationRemoveUseCase(AppMutationUseCase["VacationRemoveUseCase.Args", None]):
    """The command for removing a vacation."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId

    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        vacation_notion_manager: VacationNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._vacation_notion_manager = vacation_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            vacation = uow.vacation_repository.load_by_id(args.ref_id)
        vacation_remove_service = VacationRemoveService(
            self._storage_engine, self._vacation_notion_manager
        )
        vacation_remove_service.do_it(progress_reporter, vacation)
