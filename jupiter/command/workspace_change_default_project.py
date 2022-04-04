"""UseCase for changing the default project the workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectUseCase,
)

LOGGER = logging.getLogger(__name__)


class WorkspaceChangeDefaultProject(command.Command):
    """UseCase class for changing the default project of the workspace."""

    _command: Final[WorkspaceChangeDefaultProjectUseCase]

    def __init__(self, the_command: WorkspaceChangeDefaultProjectUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-change-default-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--default-project-key",
            dest="default_project_key",
            required=True,
            help="The key of the default project",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        default_project_key = ProjectKey.from_raw(args.default_project_key)
        self._command.execute(
            WorkspaceChangeDefaultProjectUseCase.Args(
                default_project_key=default_project_key
            )
        )
