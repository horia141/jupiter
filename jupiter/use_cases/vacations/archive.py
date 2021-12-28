"""The command for archiving a vacation."""
import logging
from typing import Final

from jupiter.domain.vacations.infra.vacation_engine import VacationEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class VacationArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a vacation."""

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

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as uow:
            vacation = uow.vacation_repository.load_by_id(args)
            vacation.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.vacation_repository.save(vacation)

        try:
            self._notion_manager.remove_vacation(vacation.ref_id)
        except NotionVacationNotFoundError:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")
