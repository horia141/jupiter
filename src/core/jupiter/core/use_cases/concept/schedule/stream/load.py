"""Use case for loading a particular stream."""

from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
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
class ScheduleStreamLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class ScheduleStreamLoadResult(UseCaseResultBase):
    """Result."""

    schedule_stream: ScheduleStream
    note: Note | None


@readonly_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleStreamLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        ScheduleStreamLoadArgs, ScheduleStreamLoadResult
    ]
):
    """Use case for loading a particular stream."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ScheduleStreamLoadArgs,
    ) -> ScheduleStreamLoadResult:
        """Execute the command's action."""
        schedule_stream = await uow.get_for(ScheduleStream).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.SCHEDULE_STREAM,
            schedule_stream.ref_id,
            allow_archived=args.allow_archived,
        )

        return ScheduleStreamLoadResult(schedule_stream=schedule_stream, note=note)
