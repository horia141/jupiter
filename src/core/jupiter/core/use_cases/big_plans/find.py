"""The command for finding a big plan."""
from collections import defaultdict

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
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
class BigPlanFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_project: bool
    include_inbox_tasks: bool
    include_notes: bool
    filter_ref_ids: list[EntityId] | None
    filter_project_ref_ids: list[EntityId] | None


@use_case_result_part
class BigPlanFindResultEntry(UseCaseResultBase):
    """A single big plan result."""

    big_plan: BigPlan
    note: Note | None
    project: Project | None
    inbox_tasks: list[InboxTask] | None


@use_case_result
class BigPlanFindResult(UseCaseResultBase):
    """PersonFindResult."""

    entries: list[BigPlanFindResultEntry]


@readonly_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[BigPlanFindArgs, BigPlanFindResult]
):
    """The command for finding a big plan."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: BigPlanFindArgs,
    ) -> BigPlanFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        if args.include_project:
            projects = await uow.get_for(Project).find_all_generic(
                parent_ref_id=project_collection.ref_id,
                allow_archived=args.allow_archived,
                ref_id=args.filter_project_ref_ids or NoFilter(),
            )
            project_by_ref_id = {p.ref_id: p for p in projects}
        else:
            project_by_ref_id = None

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id,
        )
        big_plans = await uow.get_for(BigPlan).find_all_generic(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
            project_ref_id=args.filter_project_ref_ids or NoFilter(),
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                big_plan_ref_id=[bp.ref_id for bp in big_plans],
            )
        else:
            inbox_tasks = None

        notes_by_inbox_task_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.BIG_PLAN,
                allow_archived=True,
                source_entity_ref_id=[bp.ref_id for bp in big_plans],
            )
            for note in notes:
                notes_by_inbox_task_ref_id[note.source_entity_ref_id] = note

        return BigPlanFindResult(
            entries=[
                BigPlanFindResultEntry(
                    big_plan=bp,
                    project=project_by_ref_id[bp.project_ref_id]
                    if project_by_ref_id is not None
                    else None,
                    inbox_tasks=[
                        it for it in inbox_tasks if it.big_plan_ref_id == bp.ref_id
                    ]
                    if inbox_tasks is not None
                    else None,
                    note=notes_by_inbox_task_ref_id.get(bp.ref_id, None),
                )
                for bp in big_plans
            ],
        )
