"""Command for removing a recurring task."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from models.framework import EntityId
from use_cases.recurring_tasks.archive import RecurringTaskArchiveCommand

LOGGER = logging.getLogger(__name__)


class RecurringTaskArchive(command.Command):
    """Command class for removing a recurring task."""

    _command: Final[RecurringTaskArchiveCommand]

    def __init__(self, the_command: RecurringTaskArchiveCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-task-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(RecurringTaskArchiveCommand.Args(ref_id))
