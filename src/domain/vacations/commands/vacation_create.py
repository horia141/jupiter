"""The command for creating a vacation."""
from dataclasses import dataclass
from typing import Final

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from domain.vacations.vacation import Vacation
from models.basic import EntityName, ADate
from models.framework import Command
from utils.time_provider import TimeProvider


class VacationCreateCommand(Command['VacationCreateCommand.Args', None]):
    """The command for creating a vacation."""

    @dataclass()
    class Args:
        """Args."""
        name: EntityName
        start_date: ADate
        end_date: ADate

    _time_provider: Final[TimeProvider]
    _vacation_engine: Final[VacationEngine]
    _notion_manager: Final[VacationNotionManager]

    def __init__(
            self, time_provider: TimeProvider, vacation_engine: VacationEngine,
            notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._vacation_engine = vacation_engine
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's actions."""
        vacation = Vacation.new_vacation(
            False, args.name, args.start_date, args.end_date, self._time_provider.get_current_time())
        with self._vacation_engine.get_unit_of_work() as uow:
            vacation = uow.vacation_repository.create(vacation)
        self._notion_manager.upsert_vacation(vacation)
