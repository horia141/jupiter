"""Use case for finding time plans."""
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.framework.base.entity_id import EntityId
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
class TimePlanFindArgs(UseCaseArgsBase):
    """Args."""

    allow_archived: bool
    include_notes: bool
    filter_ref_ids: list[EntityId] | None


@use_case_result_part
class TimePlanFindResultEntry(UseCaseResultBase):
    """Result part."""

    time_plan: TimePlan
    note: Note | None


@use_case_result
class TimePlanFindResult(UseCaseResultBase):
    """Result."""

    entries: list[TimePlanFindResultEntry]


@readonly_use_case(WorkspaceFeature.JOURNALS)
class TimePlanFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[TimePlanFindArgs, TimePlanFindResult]
):
    """The command for finding time plans."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanFindArgs,
    ) -> TimePlanFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id,
        )
        note_collection = await uow.get_for(NoteCollection).load_by_parent(
            workspace.ref_id,
        )
        time_plans = await uow.get_for(TimePlan).find_all(
            parent_ref_id=time_plan_domain.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        notes_by_time_plan_ref_id = {}
        if args.include_notes:
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.JOURNAL,
                allow_archived=True,
                source_entity_ref_id=[time_plan.ref_id for time_plan in time_plans],
            )
            for note in notes:
                notes_by_time_plan_ref_id[note.source_entity_ref_id] = note

        return TimePlanFindResult(
            entries=[
                TimePlanFindResultEntry(
                    time_plan=time_plan,
                    note=notes_by_time_plan_ref_id.get(time_plan.ref_id, None),
                )
                for time_plan in time_plans
            ]
        )
