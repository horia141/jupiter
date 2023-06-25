"""The command for finding workspaces."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class WorkspaceLoadArgs(UseCaseArgsBase):
    """Workspace find args."""


@dataclass
class WorkspaceLoadResult(UseCaseResultBase):
    """PersonFindResult object."""

    workspace: Workspace
    default_project: Project


class WorkspaceLoadUseCase(
    AppLoggedInReadonlyUseCase[WorkspaceLoadArgs, WorkspaceLoadResult]
):
    """The command for loading workspaces."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceLoadArgs,
    ) -> WorkspaceLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        async with self._storage_engine.get_unit_of_work() as uow:
            default_project = await uow.project_repository.load_by_id(
                workspace.default_project_ref_id,
            )
        return WorkspaceLoadResult(workspace=workspace, default_project=default_project)
