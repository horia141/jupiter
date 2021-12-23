"""The command for finding workspaces."""
from dataclasses import dataclass
from typing import Final

from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project import Project
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from domain.workspaces.workspace import Workspace
from framework.use_case import UseCase


class WorkspaceFindUseCase(UseCase[None, 'WorkspaceFindUseCase.Response']):
    """The command for finding workspaces."""

    @dataclass()
    class Response:
        """Response object."""

        workspace: Workspace
        default_project: Project

    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]

    def __init__(
            self, workspace_engine: WorkspaceEngine, project_engine: ProjectEngine) -> None:
        """Constructor."""
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine

    def execute(self, args: None) -> 'Response':
        """Execute the command's action."""
        with self._workspace_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
        with self._project_engine.get_unit_of_work() as project_uow:
            default_project = project_uow.project_repository.load_by_id(workspace.default_project_ref_id)
        return self.Response(workspace=workspace, default_project=default_project)
