"""UseCase for unsuspending of a recurring task."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import jupiter.command.command as command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.recurring_tasks.suspend import RecurringTaskSuspendUseCase

LOGGER = logging.getLogger(__name__)


class RecurringTaskUnsuspend(command.Command):
    """UseCase class for unsuspending a recurring task."""

    _command: Final[RecurringTaskSuspendUseCase]

    def __init__(self, the_command: RecurringTaskSuspendUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-task-unsuspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Unsuspend a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the recurring task to modify")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(RecurringTaskSuspendUseCase.Args(ref_id, False))
