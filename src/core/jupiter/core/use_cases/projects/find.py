"""The command for finding projects."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ProjectFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class ProjectFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    projects: List[Project]


class ProjectFindUseCase(
    AppLoggedInReadonlyUseCase[ProjectFindArgs, ProjectFindResult]
):
    """The command for finding projects."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: ProjectFindArgs,
    ) -> ProjectFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            projects = await uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
            )

        return ProjectFindResult(projects=list(projects))
