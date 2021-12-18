"""The command for finding vacations."""
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.vacation import Vacation
from models.framework import Command, EntityId


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

    _vacation_engine: Final[VacationEngine]

    def __init__(self, vacation_engine: VacationEngine) -> None:
        """Constructor."""
        self._vacation_engine = vacation_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as uow:
            vacations = uow.vacation_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids)
        return self.Response(vacations=vacations)
