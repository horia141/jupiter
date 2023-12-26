"""The command for finding workspaces."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
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
class WorkspaceLoadArgs(UseCaseArgsBase):
    """Workspace find args."""


@dataclass
class WorkspaceLoadResult(UseCaseResultBase):
    """PersonFindResult object."""

    workspace: Workspace
    default_project: Project


@readonly_use_case()
class WorkspaceLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[WorkspaceLoadArgs, WorkspaceLoadResult]
):
    """The command for loading workspaces."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: WorkspaceLoadArgs,
    ) -> WorkspaceLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        default_project = await uow.project_repository.load_by_id(
            workspace.default_project_ref_id,
        )
        return WorkspaceLoadResult(workspace=workspace, default_project=default_project)
