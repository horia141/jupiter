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
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class VacationCreateUseCase(UseCase['VacationCreateUseCase.Args', None]):
    """The command for creating a vacation."""

    @dataclass()
    class Args:
        """Args."""
        name: VacationName
        start_date: ADate
        end_date: ADate

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._vacation_notion_manager = notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's actions."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

            vacation = Vacation.new_vacation(
                archived=False, workspace_ref_id=workspace.ref_id, name=args.name, start_date=args.start_date,
                end_date=args.end_date, source=EventSource.CLI, created_time=self._time_provider.get_current_time())

            vacation = uow.vacation_repository.create(vacation)
        notion_vacation = NotionVacation.new_notion_row(vacation, None)
        self._vacation_notion_manager.upsert_vacation(notion_vacation)
