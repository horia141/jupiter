"""Use case for removing a calendar stream."""
from jupiter.core.domain.concept.calendar.calendar_domain import CalendarDomain
from jupiter.core.domain.concept.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.concept.calendar.calendar_stream_source import CalendarStreamSource
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
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
class CalendarStreamRemoveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarStreamRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[CalendarStreamRemoveArgs, None]
):
    """Use case for removing a calendar stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarStreamRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        calendar_stream = await uow.get_for(CalendarStream).load_by_id(
            args.ref_id, allow_archived=True
        )
        if calendar_stream.source == CalendarStreamSource.USER:
            calendar_domain = await uow.get_for(CalendarDomain).load_by_parent(
                workspace.ref_id
            )
            all_user_calendar_streams = await uow.get_for(
                CalendarStream
            ).find_all_generic(
                parent_ref_id=calendar_domain.ref_id,
                source=CalendarStreamSource.USER,
                allow_removed=False,
            )

            if len(all_user_calendar_streams) == 1:
                raise InputValidationError("You cannot remove the last user calendar")

        await generic_crown_remover(
            context.domain_context, uow, progress_reporter, CalendarStream, args.ref_id
        )
