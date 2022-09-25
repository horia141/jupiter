"""UseCase for showing the projects."""
from argparse import Namespace, ArgumentParser
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_key_to_rich_text,
    entity_name_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.projects.find import ProjectFindUseCase


class ProjectShow(command.ReadonlyCommand):
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

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        project_keys = (
            [ProjectKey.from_raw(pk) for pk in args.project_keys]
            if len(args.project_keys) > 0
            else None
        )

        result = self._command.execute(
            progress_reporter,
            ProjectFindUseCase.Args(
                allow_archived=show_archived, filter_keys=project_keys
            ),
        )

        sorted_projects = sorted(
            result.projects,
            key=lambda pe: (pe.archived, pe.created_time),
        )

        rich_tree = Tree("💡 Projects", guide_style="bold bright_blue")

        for project in sorted_projects:
            project_text = Text("")
            project_text.append(entity_key_to_rich_text(project.key))
            project_text.append(" ")
            project_text.append(entity_name_to_rich_text(project.name))

            if project.archived:
                project_text.stylize("gray62")

            rich_tree.add(project_text)

        console = Console()
        console.print(rich_tree)
