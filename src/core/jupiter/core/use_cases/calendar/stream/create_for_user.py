"""Use case for creating a calendar stream."""
from jupiter.core.domain.calendar.calendar_domain import CalendarDomain
from jupiter.core.domain.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.calendar.calendar_stream_color import CalendarStreamColor
from jupiter.core.domain.calendar.calendar_stream_name import CalendarStreamName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class CalendarStreamCreateForUserArgs(UseCaseArgsBase):
    """Args."""

    name: CalendarStreamName
    color: CalendarStreamColor


@use_case_result
class CalendarStreamCreateForUserResult(UseCaseResultBase):
    """Result."""

    new_calendar_stream: CalendarStream


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarStreamCreateForUserUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarStreamCreateForUserArgs, CalendarStreamCreateForUserResult
    ]
):
    """Use case for creating a calendar stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarStreamCreateForUserArgs,
    ) -> CalendarStreamCreateForUserResult:
        """Perform the transactional mutation."""
        workspace = context.workspace
        calendar_domain = await uow.get_for(CalendarDomain).load_by_parent(
            workspace.ref_id
        )
        calendar_stream = CalendarStream.new_calendar_stream_for_user(
            context.domain_context,
            calendar_domain_ref_id=calendar_domain.ref_id,
            name=args.name,
            color=args.color,
        )
        await generic_creator(uow, progress_reporter, calendar_stream)
        return CalendarStreamCreateForUserResult(new_calendar_stream=calendar_stream)
