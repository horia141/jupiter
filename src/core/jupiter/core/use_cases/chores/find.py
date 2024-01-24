"""The command for finding a chore."""
from typing import List, Optional

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class ChoreFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_project: bool
    include_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_project_ref_ids: Optional[List[EntityId]] = None


@use_case_result_part
class ChoreFindResultEntry:
    """A single entry in the load all chores response."""

    chore: Chore
    project: Optional[Project] = None
    inbox_tasks: Optional[List[InboxTask]] = None


@use_case_result
class ChoreFindResult(UseCaseResultBase):
    """The result."""

    entries: List[ChoreFindResultEntry]


@readonly_use_case(WorkspaceFeature.CHORES)
class ChoreFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[ChoreFindArgs, ChoreFindResult]
):
    """The command for finding a chore."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ChoreFindArgs,
    ) -> ChoreFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        project_collection = await uow.project_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        if args.include_project:
            projects = await uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                filter_ref_ids=args.filter_project_ref_ids,
            )
            project_by_ref_id = {p.ref_id: p for p in projects}
        else:
            project_by_ref_id = None

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        chore_collection = await uow.chore_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        chores = await uow.chore_repository.find_all_with_filters(
            parent_ref_id=chore_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
            filter_project_ref_ids=args.filter_project_ref_ids,
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_chore_ref_ids=(bp.ref_id for bp in chores),
            )
        else:
            inbox_tasks = None

        return ChoreFindResult(
            entries=[
                ChoreFindResultEntry(
                    chore=rt,
                    project=project_by_ref_id[rt.project_ref_id]
                    if project_by_ref_id is not None
                    else None,
                    inbox_tasks=[
                        it for it in inbox_tasks if it.chore_ref_id == rt.ref_id
                    ]
                    if inbox_tasks is not None
                    else None,
                )
                for rt in chores
            ],
        )
