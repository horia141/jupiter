"""UseCase for showing the projects."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.projects.find import ProjectFindUseCase

LOGGER = logging.getLogger(__name__)


class ProjectShow(command.Command):
    """UseCase class for showing the projects."""

    _command: Final[ProjectFindUseCase]

    def __init__(self, the_command: ProjectFindUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "project-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the projects"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )
        parser.add_argument(
            "--project",
            dest="project_keys",
            default=[],
            action="append",
            help="The project key to show",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        project_keys = (
            [ProjectKey.from_raw(pk) for pk in args.project_keys]
            if len(args.project_keys) > 0
            else None
        )
        response = self._command.execute(
            ProjectFindUseCase.Args(
                allow_archived=show_archived, filter_keys=project_keys
            )
        )

        for project in response.projects:
            print(f"{project.key}: {project.name}")
