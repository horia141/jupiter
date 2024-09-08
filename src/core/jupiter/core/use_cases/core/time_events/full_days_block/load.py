"""Load a full day block and associated data."""
from jupiter.core.domain.concept.persons.person import Person
from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
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
class FullDaysBlockLoadArgs(UseCaseArgsBase):
    """FullDaysBlockLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class FullDaysBlockLoadResult(UseCaseResultBase):
    """FullDaysBlockLoadResult."""

    full_days_block: TimeEventFullDaysBlock
    schedule_event: ScheduleEventFullDays | None
    person: Person | None


@readonly_use_case()
class FullDaysBlockLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        FullDaysBlockLoadArgs, FullDaysBlockLoadResult
    ]
):
    """Load a full day block and associated data."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: FullDaysBlockLoadArgs,
    ) -> FullDaysBlockLoadResult:
        """Load a full day block and associated data."""
        full_days_block = await uow.get_for(TimeEventFullDaysBlock).load_by_id(
            args.ref_id,
            allow_archived=args.allow_archived,
        )

        schedule_event = None
        if full_days_block.namespace == TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK:
            schedule_event = await uow.get_for(ScheduleEventFullDays).load_by_id(
                full_days_block.source_entity_ref_id,
                allow_archived=args.allow_archived,
            )

        person = None
        if full_days_block.namespace == TimeEventNamespace.PERSON_BIRTHDAY:
            person = await uow.get_for(Person).load_by_id(
                full_days_block.source_entity_ref_id,
                allow_archived=args.allow_archived,
            )

        return FullDaysBlockLoadResult(
            full_days_block=full_days_block,
            schedule_event=schedule_event,
            person=person,
        )
