"""Usecase for finding schedule streams."""

from collections import defaultdict

from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class ScheduleStreamFindArgs(UseCaseArgsBase):
    """Args."""

    include_notes: bool
    allow_archived: bool
    filter_ref_ids: list[EntityId] | None


@use_case_result_part
class ScheduleStreamFindResultEntry(UseCaseResultBase):
    """A single entry in the load all schedule streams response."""

    schedule_stream: ScheduleStream
    note: Note | None


@use_case_result
class ScheduleStreamFindResult(UseCaseResultBase):
    """The result."""

    entries: list[ScheduleStreamFindResultEntry]


@readonly_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleStreamFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        ScheduleStreamFindArgs, ScheduleStreamFindResult
    ]
):
    """Usecase for finding schedule streams."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ScheduleStreamFindArgs,
    ) -> ScheduleStreamFindResult:
        """Perform the transactional read."""
        workspace = context.workspace
        schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
            workspace.ref_id
        )
        schedule_streams = await uow.get_for(ScheduleStream).find_all_generic(
            parent_ref_id=schedule_domain.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
        )

        notes_by_schedule_stream_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.SCHEDULE_STREAM,
                allow_archived=True,
                source_entity_ref_id=[cs.ref_id for cs in schedule_streams],
            )
            for n in notes:
                notes_by_schedule_stream_ref_id[n.source_entity_ref_id] = n

        return ScheduleStreamFindResult(
            entries=[
                ScheduleStreamFindResultEntry(
                    schedule_stream=cs,
                    note=notes_by_schedule_stream_ref_id.get(cs.ref_id, None),
                )
                for cs in schedule_streams
            ]
        )
