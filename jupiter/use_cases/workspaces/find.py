"""The command for finding workspaces."""
from dataclasses import dataclass

from jupiter.domain.projects.project import Project
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class WorkspaceFindUseCase(
    AppReadonlyUseCase["WorkspaceFindUseCase.Args", "WorkspaceFindUseCase.Result"]
):
    """The command for finding workspaces."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result object."""

        workspace: Workspace
        default_project: Project

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            default_project = uow.project_repository.load_by_id(
                workspace.default_project_ref_id
            )
        return self.Result(workspace=workspace, default_project=default_project)
