"""Use case for changing the schedule stream of an event."""
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.features import WorkspaceFeature
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
class ScheduleEventInDayChangeScheduleStreamArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    schedule_stream_ref_id: EntityId


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventInDayChangeScheduleStreamUseCase(
    AppTransactionalLoggedInMutationUseCase[ScheduleEventInDayChangeScheduleStreamArgs, None]
):
    """Use case for changing the schedule stream of an event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventInDayChangeScheduleStreamArgs,
    ) -> None:
        """Execute the command's action."""
        _ = await uow.get_for(ScheduleStream).load_by_id(args.schedule_stream_ref_id)
        schedule_event_in_day = await uow.get_for(ScheduleEventInDay).load_by_id(
            args.ref_id
        )
        schedule_event_in_day = schedule_event_in_day.change_schedule_stream(
            context.domain_context,
            schedule_stream_ref_id=args.schedule_stream_ref_id,
        )
        schedule_event_in_day = await uow.get_for(ScheduleEventInDay).save(
            schedule_event_in_day
        )
        await progress_reporter.mark_updated(schedule_event_in_day)
