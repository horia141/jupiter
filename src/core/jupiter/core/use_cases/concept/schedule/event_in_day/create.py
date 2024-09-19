"""Use case for creating a schedule in day event."""
from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
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
class ScheduleEventInDayCreateArgs(UseCaseArgsBase):
    """Args."""

    schedule_stream_ref_id: EntityId
    name: ScheduleEventName
    start_date: ADate
    start_time_in_day: TimeInDay
    duration_mins: int


@use_case_result
class ScheduleEventInDayCreateResult(UseCaseResultBase):
    """Result."""

    new_schedule_event_in_day: ScheduleEventInDay
    new_time_event_in_day_block: TimeEventInDayBlock


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventInDayCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        ScheduleEventInDayCreateArgs, ScheduleEventInDayCreateResult
    ]
):
    """Use case for creating a schedule in day event."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventInDayCreateArgs,
    ) -> ScheduleEventInDayCreateResult:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace
        schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
            workspace.ref_id
        )
        schedule_stream = await uow.get_for(ScheduleStream).load_by_id(
            args.schedule_stream_ref_id
        )

        if not schedule_stream.can_be_modified_independently:
            raise InputValidationError(
                "Cannot create an event for a schedule stream that can't be modified."
            )

        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id
        )

        new_schedule_event_in_day = (
            ScheduleEventInDay.new_schedule_event_in_day_for_user(
                context.domain_context,
                schedule_domain_ref_id=schedule_domain.ref_id,
                schedule_stream_ref_id=schedule_stream.ref_id,
                name=args.name,
            )
        )
        new_schedule_event_in_day = await generic_creator(
            uow, progress_reporter, new_schedule_event_in_day
        )

        new_time_event_in_day_block = (
            TimeEventInDayBlock.new_time_event_for_schedule_event(
                context.domain_context,
                time_event_domain_ref_id=time_event_domain.ref_id,
                schedule_event_ref_id=new_schedule_event_in_day.ref_id,
                start_date=args.start_date,
                start_time_in_day=args.start_time_in_day,
                duration_mins=args.duration_mins,
                timezone=user.timezone,
            )
        )
        new_time_event_in_day_block = await uow.get_for(TimeEventInDayBlock).create(
            new_time_event_in_day_block
        )

        return ScheduleEventInDayCreateResult(
            new_schedule_event_in_day=new_schedule_event_in_day,
            new_time_event_in_day_block=new_time_event_in_day_block,
        )
