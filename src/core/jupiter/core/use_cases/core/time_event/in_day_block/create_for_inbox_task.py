"""Use case for creating a time event associated with an inbox task."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_in_day import TimeInDay
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
class TimeEventInDayBlockCreateForInboxTaskArgs(UseCaseArgsBase):
    """Args."""

    inbox_task_ref_id: EntityId
    start_date: ADate
    start_time_in_day: TimeInDay
    duration_mins: int


@use_case_result
class TimeEventInDayBlockCreateForInboxTaskResult(UseCaseResultBase):
    """Result."""

    new_time_event: TimeEventInDayBlock


@mutation_use_case()
class TimeEventInDayBlockCreateForInboxTaskUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimeEventInDayBlockCreateForInboxTaskArgs,
        TimeEventInDayBlockCreateForInboxTaskResult,
    ]
):
    """Use case for creating a time event associated with an inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimeEventInDayBlockCreateForInboxTaskArgs,
    ) -> TimeEventInDayBlockCreateForInboxTaskResult:
        """Execute the command's action."""
        workspace = context.workspace
        time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
            workspace.ref_id
        )

        inbox_task = await uow.get_for(InboxTask).load_by_id(args.inbox_task_ref_id)

        new_time_event = TimeEventInDayBlock.new_time_event_for_inbox_task(
            context.domain_context,
            time_event_domain_ref_id=time_event_domain.ref_id,
            inbox_task_ref_id=inbox_task.ref_id,
            start_date=args.start_date,
            start_time_in_day=args.start_time_in_day,
            duration_mins=args.duration_mins,
        )
        new_time_event = await uow.get_for(TimeEventInDayBlock).create(new_time_event)

        return TimeEventInDayBlockCreateForInboxTaskResult(
            new_time_event=new_time_event
        )
