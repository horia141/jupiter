"""Use case for updateing a full day block in the calendar."""
from jupiter.core.domain.calendar.calendar_event_full_days import CalendarEventFullDays
from jupiter.core.domain.calendar.calendar_event_name import CalendarEventName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
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
class CalendarEventFullDaysUpdateArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    name: UpdateAction[CalendarEventName]
    start_date: UpdateAction[ADate]
    duration_days: UpdateAction[int]


@mutation_use_case(WorkspaceFeature.CALENDAR)
class CalendarEventFullDaysUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[CalendarEventFullDaysUpdateArgs, None]
):
    """Use case for updating a full day block in the calendar."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: CalendarEventFullDaysUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        calendar_event_full_days = await uow.get_for(CalendarEventFullDays).load_by_id(
            args.ref_id
        )
        calendar_event_full_days = calendar_event_full_days.update(
            context.domain_context,
            name=args.name,
        )
        calendar_event_full_days = await uow.get_for(CalendarEventFullDays).save(
            calendar_event_full_days
        )
        await progress_reporter.mark_updated(calendar_event_full_days)

        time_event = await uow.get(TimeEventFullDaysBlockRepository).load_for_namespace(
            namespace=TimeEventNamespace.CALENDAR_FULL_DAY_BLOCK,
            source_entity_ref_id=calendar_event_full_days.ref_id,
        )
        time_event = time_event.update(
            context.domain_context,
            start_date=args.start_date.or_else(time_event.start_date),
            duration_days=args.duration_days.or_else(time_event.duration_days),
        )
        await uow.get_for(TimeEventFullDaysBlock).save(time_event)
