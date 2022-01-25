"""The command for creating a vacation."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.adate import ADate
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.notion_vacation import NotionVacation
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class VacationCreateUseCase(AppMutationUseCase['VacationCreateUseCase.Args', None]):
    """The command for creating a vacation."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        name: VacationName
        start_date: ADate
        end_date: ADate

    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._vacation_notion_manager = notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's actions."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

            vacation = Vacation.new_vacation(
                archived=False, workspace_ref_id=workspace.ref_id, name=args.name, start_date=args.start_date,
                end_date=args.end_date, source=EventSource.CLI, created_time=self._time_provider.get_current_time())

            vacation = uow.vacation_repository.create(vacation)
        notion_vacation = NotionVacation.new_notion_row(vacation, None)
        self._vacation_notion_manager.upsert_vacation(notion_vacation)
