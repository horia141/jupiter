"""Use case for archiving a calendar stream."""
from jupiter.core.domain.calendar.calendar_domain import CalendarDomain
from jupiter.core.domain.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.calendar.calendar_stream_source import CalendarStreamSource
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_archiver import generic_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class CalendarStreamArchiveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarStreamArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarStreamArchiveArgs, None
    ]
):
    """Use case for archiving a calendar stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarStreamArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        calendar_stream = await uow.get_for(CalendarStream).load_by_id(args.ref_id)
        if calendar_stream.source == CalendarStreamSource.USER:
            calendar_domain = await uow.get_for(CalendarDomain).load_by_parent(workspace.ref_id)
            all_user_calendars = await uow.get_for(CalendarStream).find_all_generic(
                parent_ref_id=calendar_domain.ref_id,
                source=CalendarStreamSource.USER,
                allow_archived=False
            )

            if len(all_user_calendars) == 1:
                raise InputValidationError("You cannot archive the last user calendar")

        await generic_archiver(context.domain_context, uow, progress_reporter, CalendarStream, args.ref_id)
