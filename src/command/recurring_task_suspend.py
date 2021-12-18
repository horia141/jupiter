"""Command for suspending of a recurring task."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from models.framework import EntityId
from use_cases.recurring_tasks.suspend import RecurringTaskSuspendCommand

LOGGER = logging.getLogger(__name__)


class RecurringTaskSuspend(command.Command):
    """Command class for suspending a recurring task."""

    _command: Final[RecurringTaskSuspendCommand]

    def __init__(self, the_command: RecurringTaskSuspendCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-task-suspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Suspend a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the recurring task to modify")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(RecurringTaskSuspendCommand.Args(ref_id, True))
