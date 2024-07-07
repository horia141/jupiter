"""Use case for creating a full day block in the calendar."""
from jupiter.core.domain.concept.calendar.calendar_domain import CalendarDomain
from jupiter.core.domain.concept.calendar.calendar_event_full_days import (
    CalendarEventFullDays,
)
from jupiter.core.domain.concept.calendar.calendar_event_name import CalendarEventName
from jupiter.core.domain.concept.calendar.calendar_stream import CalendarStream
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
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
class CalendarEventFullDaysCreateArgs(UseCaseArgsBase):
    """Args."""

    calendar_stream_ref_id: EntityId
    name: CalendarEventName
    start_date: ADate
    duration_days: int


@use_case_result
class CalendarEventFullDaysCreateResult(UseCaseResultBase):
    """Result."""

    new_calendar_event_full_days: CalendarEventFullDays
    new_time_event_full_day_block: TimeEventFullDaysBlock


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarEventFullDaysCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarEventFullDaysCreateArgs, CalendarEventFullDaysCreateResult
    ]
):
    """Use case for creating a full day event in the calendar."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventFullDaysCreateArgs,
    ) -> CalendarEventFullDaysCreateResult:
        """Execute the command's action."""
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

        new_calendar_event_full_days = (
            CalendarEventFullDays.new_calendar_full_days_block(
                context.domain_context,
                calendar_domain_ref_id=calendar_domain.ref_id,
                calendar_stream_ref_id=calendar_stream.ref_id,
                name=args.name,
            )
        )
        new_calendar_event_full_days = await generic_creator(
            uow, progress_reporter, new_calendar_event_full_days
        )

        new_time_event_full_days_block = TimeEventFullDaysBlock.new_time_event(
            context.domain_context,
            time_event_domain_ref_id=time_event_domain.ref_id,
            namespace=TimeEventNamespace.CALENDAR_FULL_DAY_BLOCK,
            source_entity_ref_id=new_calendar_event_full_days.ref_id,
            start_date=args.start_date,
            duration_days=args.duration_days,
        )
        new_time_event_full_days_block = await generic_creator(
            uow, progress_reporter, new_time_event_full_days_block
        )

        return CalendarEventFullDaysCreateResult(
            new_calendar_event_full_days=new_calendar_event_full_days,
            new_time_event_full_day_block=new_time_event_full_days_block,
        )
