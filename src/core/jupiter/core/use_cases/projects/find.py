"""The command for finding projects."""
from typing import List, Optional

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
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
class ProjectFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@use_case_result
class ProjectFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    projects: List[Project]


@readonly_use_case(WorkspaceFeature.PROJECTS)
class ProjectFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[ProjectFindArgs, ProjectFindResult]
):
    """The command for finding projects."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ProjectFindArgs,
    ) -> ProjectFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        project_collection = await uow.project_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        projects = await uow.project_repository.find_all_with_filters(
            parent_ref_id=project_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        return ProjectFindResult(projects=list(projects))
