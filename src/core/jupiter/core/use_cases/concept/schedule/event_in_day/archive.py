"""Use case for archiving a schedule in day event."""
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_archiver import generic_crown_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ScheduleEventInDayArchiveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventInDayArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[ScheduleEventInDayArchiveArgs, None]
):
    """Use case for archiving a schedule in day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventInDayArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        schedule_event_in_day = await uow.get_for(ScheduleEventInDay).load_by_id(
            args.ref_id
        )
        if not schedule_event_in_day.can_be_modified_independently:
            raise InputValidationError("Cannot archive a non-user schedule event")
        await generic_crown_archiver(
            context.domain_context,
            uow,
            progress_reporter,
            ScheduleEventInDay,
            args.ref_id,
        )
