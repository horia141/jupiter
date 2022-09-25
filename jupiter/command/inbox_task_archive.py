"""UseCase for archiving an inbox task."""
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.inbox_tasks.archive import InboxTaskArchiveUseCase


class InboxTaskArchive(command.Command):
    """UseCase class for archiving an inbox task."""

    _command: Final[InboxTaskArchiveUseCase]

    def __init__(self, the_command: InboxTaskArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "inbox-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive an inbox task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The if of the big plan",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)

        self._command.execute(progress_reporter, InboxTaskArchiveUseCase.Args(ref_id))
