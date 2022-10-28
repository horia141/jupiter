"""UseCase for hard remove email tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.email.remove import EmailTaskRemoveUseCase


class EmailTaskRemove(command.Command):
    """UseCase class for hard removing email tasks."""

    _command: Final[EmailTaskRemoveUseCase]

    def __init__(self, the_command: EmailTaskRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove email tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="Remove this email task",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, EmailTaskRemoveUseCase.Args(ref_id))
