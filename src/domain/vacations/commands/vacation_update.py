"""The command for updating a vacation's properties."""
from dataclasses import dataclass
from typing import Final

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from models.basic import EntityName, EntityId, ADate
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider


class VacationUpdateCommand(Command['VacationUpdateCommand.Args', None]):
    """The command for updating a vacation's properties."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[EntityName]
        start_date: UpdateAction[ADate]
        end_date: UpdateAction[ADate]

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
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as uow:
            vacation = uow.vacation_repository.get_by_id(args.ref_id)

            if args.name.should_change:
                vacation.change_name(args.name.value, self._time_provider.get_current_time())
            if args.start_date.should_change:
                vacation.change_start_date(args.start_date.value, self._time_provider.get_current_time())
            if args.end_date.should_change:
                vacation.change_end_date(args.end_date.value, self._time_provider.get_current_time())

            uow.vacation_repository.save(vacation)

        self._notion_manager.upsert_vacation(vacation)
