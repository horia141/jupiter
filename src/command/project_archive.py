"""Command for removing a project."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.projects.project_key import ProjectKey
from use_cases.projects.archive import ProjectArchiveCommand

LOGGER = logging.getLogger(__name__)


class ProjectArchive(command.Command):
    """Command class for archiving a project."""

    _command: Final[ProjectArchiveCommand]

    def __init__(self, the_command: ProjectArchiveCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "project-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a project"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = ProjectKey.from_raw(args.project_key)
        self._command.execute(ProjectArchiveCommand.Args(key=project_key))
