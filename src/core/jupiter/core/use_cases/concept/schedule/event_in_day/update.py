"""Use case for updating a schedule in day event."""
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ScheduleEventInDayUpdateArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    name: UpdateAction[ScheduleEventName]
    start_date: UpdateAction[ADate]
    start_time_in_day: UpdateAction[TimeInDay]
    duration_mins: UpdateAction[int]


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventInDayUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ScheduleEventInDayUpdateArgs, None]
):
    """Use case for updating a schedule in day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventInDayUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        schedule_event_in_day = await uow.get_for(ScheduleEventInDay).load_by_id(
            args.ref_id
        )
        schedule_event_in_day = schedule_event_in_day.update(
            context.domain_context,
            name=args.name,
        )
        schedule_event_in_day = await uow.get_for(ScheduleEventInDay).save(
            schedule_event_in_day
        )
        await progress_reporter.mark_updated(schedule_event_in_day)

        time_event = await uow.get(TimeEventInDayBlockRepository).load_for_namespace(
            TimeEventNamespace.SCHEDULE_EVENT_IN_DAY, schedule_event_in_day.ref_id
        )
        time_event = time_event.update(
            context.domain_context,
            start_date=args.start_date.or_else(time_event.start_date),
            start_time_in_day=args.start_time_in_day.or_else(
                time_event.start_time_in_day
            ),
            duration_mins=args.duration_mins.or_else(time_event.duration_mins),
            timezone=time_event.timezone,
        )
        await uow.get(TimeEventInDayBlockRepository).save(time_event)
