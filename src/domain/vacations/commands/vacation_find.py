"""The command for finding vacations."""
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from domain.vacations.vacation import Vacation
from models.framework import Command, EntityId
from utils.time_provider import TimeProvider


class VacationFindCommand(Command['VacationFindCommand.Args', 'VacationFindCommand.Response']):
    """The command for finding vacations."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_ref_ids: Optional[List[EntityId]]

    @dataclass()
    class Response:
        """Response object."""

        vacations: List[Vacation]

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

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as uow:
            vacations = uow.vacation_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids)
        return self.Response(vacations=vacations)
