"""Use case for updateing a full day block in the schedule."""

from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ScheduleEventFullDaysUpdateArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    name: UpdateAction[ScheduleEventName]
    start_date: UpdateAction[ADate]
    duration_days: UpdateAction[int]


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventFullDaysUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ScheduleEventFullDaysUpdateArgs, None]
):
    """Use case for updating a full day block in the schedule."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventFullDaysUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        schedule_event_full_days = await uow.get_for(ScheduleEventFullDays).load_by_id(
            args.ref_id
        )
        if not schedule_event_full_days.can_be_modified_independently:
            raise InputValidationError("Cannot update a non-user schedule event")
        schedule_event_full_days = schedule_event_full_days.update(
            context.domain_context,
            name=args.name,
        )
        schedule_event_full_days = await uow.get_for(ScheduleEventFullDays).save(
            schedule_event_full_days
        )
        await progress_reporter.mark_updated(schedule_event_full_days)

        time_event = await uow.get(TimeEventFullDaysBlockRepository).load_for_namespace(
            namespace=TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
            source_entity_ref_id=schedule_event_full_days.ref_id,
        )
        time_event = time_event.update_for_schedule_event(
            context.domain_context,
            start_date=args.start_date,
            duration_days=args.duration_days,
        )
        await uow.get_for(TimeEventFullDaysBlock).save(time_event)
