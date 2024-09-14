"""Load an in day block with associated data."""
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class TimeEventInDayBlockLoadArgs(UseCaseArgsBase):
    """InDayBlockLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class TimeEventInDayBlockLoadResult(UseCaseResultBase):
    """InDayBlockLoadResult."""

    in_day_block: TimeEventInDayBlock
    schedule_event: ScheduleEventInDay | None
    inbox_task: InboxTask | None


@readonly_use_case()
class TimeEventInDayBlockLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        TimeEventInDayBlockLoadArgs, TimeEventInDayBlockLoadResult
    ]
):
    """Load a in day block and associated data."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimeEventInDayBlockLoadArgs,
    ) -> TimeEventInDayBlockLoadResult:
        """Load a in day block and associated data."""
        in_day_block = await uow.get_for(TimeEventInDayBlock).load_by_id(
            args.ref_id,
            allow_archived=args.allow_archived,
        )

        schedule_event = None
        if in_day_block.namespace == TimeEventNamespace.SCHEDULE_EVENT_IN_DAY:
            schedule_event = await uow.get_for(ScheduleEventInDay).load_by_id(
                in_day_block.source_entity_ref_id,
                allow_archived=args.allow_archived,
            )

        inbox_task = None
        if in_day_block.namespace == TimeEventNamespace.INBOX_TASK:
            inbox_task = await uow.get_for(InboxTask).load_by_id(
                in_day_block.source_entity_ref_id,
                allow_archived=args.allow_archived,
            )

        return TimeEventInDayBlockLoadResult(
            in_day_block=in_day_block,
            schedule_event=schedule_event,
            inbox_task=inbox_task,
        )
