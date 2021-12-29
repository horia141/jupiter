"""The command for removing a vacation entry."""
import logging
from typing import Final

from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase

LOGGER = logging.getLogger(__name__)


class VacationRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a vacation."""

    _storage_engine: Final[StorageEngine]
    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
            self, storage_engine: StorageEngine, vacation_notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._vacation_notion_manager = vacation_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            uow.vacation_repository.remove(args)

        try:
            self._vacation_notion_manager.remove_vacation(args)
        except NotionVacationNotFoundError:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")
