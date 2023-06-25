"""Shared service for removing an vacation."""
from typing import Final

from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.use_case import ContextProgressReporter


class VacationRemoveService:
    """Shared service for removing an vacation."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ContextProgressReporter,
        vacation: Vacation,
    ) -> None:
        """Execute the service's action."""
        async with progress_reporter.start_removing_entity(
            "vacation",
            vacation.ref_id,
            str(vacation.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                await uow.vacation_repository.remove(vacation.ref_id)
                await entity_reporter.mark_local_change()
