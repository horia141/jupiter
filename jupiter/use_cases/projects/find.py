"""The command for finding projects."""
from dataclasses import dataclass
from typing import Final, Optional, List

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.use_case import UseCase


class ProjectFindUseCase(UseCase['ProjectFindUseCase.Args', 'ProjectFindUseCase.Response']):
    """The command for finding projects."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_keys: Optional[List[ProjectKey]]

    @dataclass()
    class Response:
        """Response object."""

        projects: List[Project]

    _storage_engine: Final[StorageEngine]

    def __init__(self, storage_engine: StorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            projects = uow.project_repository.find_all(
                allow_archived=args.allow_archived, filter_keys=args.filter_keys)
        return self.Response(projects=list(projects))
