"""The command for removing a vacation entry."""
import logging
from typing import Final

from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from framework.entity_id import EntityId
from framework.use_case import UseCase
from remote.notion.common import CollectionEntityNotFound


LOGGER = logging.getLogger(__name__)


class VacationRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a vacation."""

    _vacation_engine: Final[VacationEngine]
    _notion_manager: Final[VacationNotionManager]

    def __init__(
            self, vacation_engune: VacationEngine, notion_manager: VacationNotionManager) -> None:
        """Constructor."""
        self._vacation_engine = vacation_engune
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as uow:
            uow.vacation_repository.remove(args)

        try:
            self._notion_manager.remove_vacation(args)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because vacation was not found")
