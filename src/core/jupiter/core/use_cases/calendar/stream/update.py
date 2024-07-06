"""Use case for updating a calendar stream."""
from jupiter.core.domain.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.calendar.calendar_stream_color import CalendarStreamColor
from jupiter.core.domain.calendar.calendar_stream_name import CalendarStreamName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class CalendarStreamUpdateArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    name: UpdateAction[CalendarStreamName]
    color: UpdateAction[CalendarStreamColor]

@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarStreamUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarStreamUpdateArgs, None
    ]
):
    """Use case for updating a calendar stream."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarStreamUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        calendar_stream = await uow.get_for(CalendarStream).load_by_id(args.ref_id)

        calendar_stream.update(
            context.domain_context,
            name=args.name,
            color=args.color,
        )

        await uow.get_for(CalendarStream).save(calendar_stream)
        await progress_reporter.mark_updated(calendar_stream)
    