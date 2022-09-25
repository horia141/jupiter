"""UseCase for updating the slack task generation project."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.command.command import Command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.push_integrations.slack.change_generation_project import (
    SlackTaskChangeGenerationProjectUseCase,
)


class SlackTaskChangeGenerationProject(Command):
    """Use case for updating the slack task generation project."""

    _command: Final[SlackTaskChangeGenerationProjectUseCase]

    def __init__(self, the_command: SlackTaskChangeGenerationProjectUseCase):
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "slack-task-change-generation-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the generation project for Slack tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        generation_project_group = parser.add_mutually_exclusive_group()
        generation_project_group.add_argument(
            "--generation-project",
            dest="generation_project_key",
            required=False,
            help="The project key to generate generation tasks",
        )
        generation_project_group.add_argument(
            "--clear-generation-project",
            dest="clear_generation_project_key",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the generation project",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        generation_project_key: Optional[ProjectKey]
        if args.clear_generation_project_key:
            generation_project_key = None
        else:
            generation_project_key = ProjectKey.from_raw(args.generation_project_key)

        self._command.execute(
            progress_reporter,
            SlackTaskChangeGenerationProjectUseCase.Args(
                generation_project_key=generation_project_key
            ),
        )
