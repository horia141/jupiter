"""The command for archiving a vacation."""
import logging
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class VacationArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a vacation."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            vacation_notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._vacation_notion_manager = vacation_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            vacation = uow.vacation_repository.load_by_id(args)
            vacation = vacation.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.vacation_repository.save(vacation)

        try:
            self._vacation_notion_manager.remove_vacation(vacation.ref_id)
        except NotionVacationNotFoundError:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")
