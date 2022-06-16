"""Shared service for removing an vacation."""
import logging
from typing import Final

from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.infra.vacation_notion_manager import (
    VacationNotionManager,
    NotionVacationNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine

LOGGER = logging.getLogger(__name__)


class VacationRemoveService:
    """Shared service for removing an vacation."""

    _storage_engine: Final[DomainStorageEngine]
    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        vacation_notion_manager: VacationNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._vacation_notion_manager = vacation_notion_manager

    def do_it(self, vacation: Vacation) -> None:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            uow.vacation_repository.remove(vacation.ref_id)
        LOGGER.info("Applied local changes")
        # Apply Notion changes
        try:
            self._vacation_notion_manager.remove_leaf(
                vacation.vacation_collection_ref_id, vacation.ref_id
            )
        except NotionVacationNotFoundError:
            LOGGER.info(
                "Skipping archiving of Notion vacation because it could not be found"
            )
