"""Shared service for removing an vacation."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.use_case import ProgressReporter


class VacationRemoveService:
    """Shared service for removing an vacation."""

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        vacation: Vacation,
    ) -> None:
        """Execute the service's action."""
        await uow.vacation_repository.remove(vacation.ref_id)
        await progress_reporter.mark_removed(vacation)
