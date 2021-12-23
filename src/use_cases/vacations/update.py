"""The command for updating a vacation's properties."""
from dataclasses import dataclass
from typing import Final

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from domain.adate import ADate
from domain.entity_name import EntityName
from framework.update_action import UpdateAction
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider


class VacationUpdateUseCase(UseCase['VacationUpdateUseCase.Args', None]):
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
            vacation = uow.vacation_repository.load_by_id(args.ref_id)

            if args.name.should_change:
                vacation.change_name(args.name.value, self._time_provider.get_current_time())
            if args.start_date.should_change:
                vacation.change_start_date(args.start_date.value, self._time_provider.get_current_time())
            if args.end_date.should_change:
                vacation.change_end_date(args.end_date.value, self._time_provider.get_current_time())

            uow.vacation_repository.save(vacation)

        self._notion_manager.upsert_vacation(vacation)
