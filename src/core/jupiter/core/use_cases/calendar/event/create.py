"""Create a calendar event."""
from jupiter.core.domain.calendar.calendar import Calendar
from jupiter.core.domain.calendar.calendar_event import CalendarEvent
from jupiter.core.domain.calendar.calendar_event_name import CalendarEventName
from jupiter.core.domain.calendar.calendar_event_type import CalendarEventType
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case


@use_case_args
class CalendarEventCreateArgs(UseCaseArgsBase):
    """CalendarEventCreate args."""

    calendar_ref_id: EntityId
    name: CalendarEventName
    the_type: CalendarEventType
    start_date: ADate | None
    start_time: Timestamp | None
    end_date: ADate | None
    end_time: Timestamp | None


@use_case_result
class CalendarEventCreateResult(UseCaseResultBase):
    """CalendarEventCreate result."""

    new_calendar_event: CalendarEvent


@mutation_use_case(WorkspaceFeature.CALENDARS)
class CalendarEventCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        CalendarEventCreateArgs, CalendarEventCreateResult
    ],
):
    """The command for creating a calendar event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventCreateArgs,
    ) -> CalendarEventCreateResult:
        """Execute the command's action."""
        calendar = await uow.get_for(Calendar).load_by_id(args.calendar_ref_id)

        new_calendar_event = CalendarEvent.new_calendar_event_for_user(
            ctx=context.domain_context,
            calendar_ref_id=calendar.ref_id,
            name=args.name,
            the_type=args.the_type,
            start_date=args.start_date,
            start_time=args.start_time,
            end_date=args.end_date,
            end_time=args.end_time,
        )

        new_calendar_event = await uow.get_for(CalendarEvent).create(new_calendar_event)
        await progress_reporter.mark_created(new_calendar_event)

        return CalendarEventCreateResult(new_calendar_event=new_calendar_event)
    