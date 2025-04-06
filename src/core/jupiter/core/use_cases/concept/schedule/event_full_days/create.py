"""Use case for creating a full day block in the schedule."""

from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
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
class ScheduleEventFullDaysCreateArgs(UseCaseArgsBase):
    """Args."""

    schedule_stream_ref_id: EntityId
    name: ScheduleEventName
    start_date: ADate
    duration_days: int


@use_case_result
class ScheduleEventFullDaysCreateResult(UseCaseResultBase):
    """Result."""

    new_schedule_event_full_days: ScheduleEventFullDays
    new_time_event_full_day_block: TimeEventFullDaysBlock


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleEventFullDaysCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        ScheduleEventFullDaysCreateArgs, ScheduleEventFullDaysCreateResult
    ]
):
    """Use case for creating a full day event in the schedule."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleEventFullDaysCreateArgs,
    ) -> ScheduleEventFullDaysCreateResult:
        """Execute the command's action."""
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

        new_schedule_event_full_days = (
            ScheduleEventFullDays.new_schedule_full_days_block_for_user(
                context.domain_context,
                schedule_domain_ref_id=schedule_domain.ref_id,
                schedule_stream_ref_id=schedule_stream.ref_id,
                name=args.name,
            )
        )
        new_schedule_event_full_days = await generic_creator(
            uow, progress_reporter, new_schedule_event_full_days
        )

        new_time_event_full_days_block = (
            TimeEventFullDaysBlock.new_time_event_for_schedule_event(
                context.domain_context,
                time_event_domain_ref_id=time_event_domain.ref_id,
                schedule_event_ref_id=new_schedule_event_full_days.ref_id,
                start_date=args.start_date,
                duration_days=args.duration_days,
            )
        )
        new_time_event_full_days_block = await uow.get_for(
            TimeEventFullDaysBlock
        ).create(new_time_event_full_days_block)

        return ScheduleEventFullDaysCreateResult(
            new_schedule_event_full_days=new_schedule_event_full_days,
            new_time_event_full_day_block=new_time_event_full_days_block,
        )
