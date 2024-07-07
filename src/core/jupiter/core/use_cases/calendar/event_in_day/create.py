"""Use case for creating a calendar in day event."""
from jupiter.core.domain.concept.calendar.calendar_domain import CalendarDomain
from jupiter.core.domain.concept.calendar.calendar_event_in_day import (
    CalendarEventInDay,
)
from jupiter.core.domain.concept.calendar.calendar_event_name import CalendarEventName
from jupiter.core.domain.concept.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class CalendarEventInDayCreateArgs(UseCaseArgsBase):
    """Args."""

    calendar_stream_ref_id: EntityId
    name: CalendarEventName
    start_date: ADate
    start_time_in_day: TimeInDay
    duration_mins: int


@use_case_result
class CalendarEventInDayCreateResult(UseCaseResultBase):
    """Result."""

    new_calendar_event_in_day: CalendarEventInDay
    new_time_event_in_day_block: TimeEventInDayBlock


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarEventInDayCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarEventInDayCreateArgs, CalendarEventInDayCreateResult
    ]
):
    """Use case for creating a calendar in day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventInDayCreateArgs,
    ) -> CalendarEventInDayCreateResult:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace
        calendar_domain = await uow.get_for(CalendarDomain).load_by_parent(
            workspace.ref_id
        )
        calendar_stream = await uow.get_for(CalendarStream).load_by_id(
            args.calendar_stream_ref_id
        )
        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id
        )

        new_calendar_event_in_day = CalendarEventInDay.new_calendar_event_in_day(
            context.domain_context,
            calendar_domain_ref_id=calendar_domain.ref_id,
            calendar_stream_ref_id=calendar_stream.ref_id,
            name=args.name,
        )
        new_calendar_event_in_day = await generic_creator(
            uow, progress_reporter, new_calendar_event_in_day
        )

        new_time_event_in_day_block = TimeEventInDayBlock.new_time_event(
            context.domain_context,
            time_event_domain_ref_id=time_event_domain.ref_id,
            namespace=TimeEventNamespace.CALENDAR_EVENT_IN_DAY,
            source_entity_ref_id=new_calendar_event_in_day.ref_id,
            start_date=args.start_date,
            start_time_in_day=args.start_time_in_day,
            duration_mins=args.duration_mins,
            timezone=user.timezone,
        )
        new_time_event_in_day_block = await generic_creator(
            uow, progress_reporter, new_time_event_in_day_block
        )

        return CalendarEventInDayCreateResult(
            new_calendar_event_in_day=new_calendar_event_in_day,
            new_time_event_in_day_block=new_time_event_in_day_block,
        )
