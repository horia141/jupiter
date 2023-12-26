"""Use case for loading a particular project."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@dataclass
class ProjectLoadArgs(UseCaseArgsBase):
    """ProjectLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class ProjectLoadResult(UseCaseResultBase):
    """ProjectLoadResult."""

    project: Project


@readonly_use_case(WorkspaceFeature.PROJECTS)
class ProjectLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[ProjectLoadArgs, ProjectLoadResult]
):
    """Use case for loading a particular project."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: ProjectLoadArgs,
    ) -> ProjectLoadResult:
        """Execute the command's action."""
        project = await uow.project_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        return ProjectLoadResult(project=project)
