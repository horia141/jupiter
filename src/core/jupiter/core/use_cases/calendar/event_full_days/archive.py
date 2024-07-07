"""Use case for archiving a calendar full day event."""
from jupiter.core.domain.concept.calendar.calendar_event_full_days import (
    CalendarEventFullDays,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_archiver import generic_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class CalendarEventFullDaysArchiveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarEventFullDaysArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[CalendarEventFullDaysArchiveArgs, None]
):
    """Use case for archiving a calendar full day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventFullDaysArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_archiver(
            context.domain_context,
            uow,
            progress_reporter,
            CalendarEventFullDays,
            args.ref_id,
        )
