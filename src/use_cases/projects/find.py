"""The command for finding projects."""
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from models.framework import Command


class ProjectFindCommand(Command['ProjectFindCommand.Args', 'ProjectFindCommand.Response']):
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

    _project_engine: Final[ProjectEngine]

    def __init__(self, project_engine: ProjectEngine) -> None:
        """Constructor."""
        self._project_engine = project_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._project_engine.get_unit_of_work() as uow:
            projects = uow.project_repository.find_all(
                allow_archived=args.allow_archived, filter_keys=args.filter_keys)
        return self.Response(projects=list(projects))
