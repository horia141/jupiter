"""The command for finding workspaces."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.projects.project import Project
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.use_case import UseCase


class WorkspaceFindUseCase(UseCase[None, 'WorkspaceFindUseCase.Response']):
    """The command for finding workspaces."""

    @dataclass()
    class Response:
        """Response object."""

        workspace: Workspace
        default_project: Project

    _storage_engine: Final[DomainStorageEngine]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: None) -> 'Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            default_project = uow.project_repository.load_by_id(workspace.default_project_ref_id)
        return self.Response(workspace=workspace, default_project=default_project)
