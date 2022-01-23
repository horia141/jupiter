"""UseCase for changing the default workspace of a project."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class WorkspaceChangeDefaultProjectUseCase(UseCase['WorkspaceChangeDefaultProjectUseCase.Args', None]):
    """UseCase for changing the default project of a workspace."""

    @dataclass()
    class Args:
        """Args."""
        default_project_key: ProjectKey

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            project = uow.project_repository.load_by_key(args.default_project_key)

            workspace = workspace.change_default_project(
                default_project_ref_id=project.ref_id,
                source=EventSource.CLI, modification_time=self._time_provider.get_current_time())

            uow.workspace_repository.save(workspace)
