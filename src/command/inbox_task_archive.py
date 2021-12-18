"""Command for archiving an inbox task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from models.framework import EntityId
from use_cases.inbox_tasks.archive import InboxTaskArchiveCommand

LOGGER = logging.getLogger(__name__)


class InboxTaskArchive(command.Command):
    """Command class for archiving an inbox task."""

    _command: Final[InboxTaskArchiveCommand]

    def __init__(self, the_command: InboxTaskArchiveCommand) -> None:
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
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The if of the big plan")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(InboxTaskArchiveCommand.Args(ref_id))
