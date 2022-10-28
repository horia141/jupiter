"""UseCase for archiving a email task."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.push_integrations.email.archive import EmailTaskArchiveUseCase


class EmailTaskArchive(command.Command):
    """UseCase class for archiving an email task."""

    _command: Final[EmailTaskArchiveUseCase]

    def __init__(self, the_command: EmailTaskArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "email-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive an email task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The if of the email task",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, EmailTaskArchiveUseCase.Args(ref_id))
