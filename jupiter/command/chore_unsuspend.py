"""UseCase for unsuspending of a chore."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.chores.unsuspend import ChoreUnsuspendUseCase

LOGGER = logging.getLogger(__name__)


class ChoreUnsuspend(command.Command):
    """UseCase class for unsuspending a chore."""

    _command: Final[ChoreUnsuspendUseCase]

    def __init__(self, the_command: ChoreUnsuspendUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-unsuspend"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Unsuspend a chore"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the chore to modify",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(ChoreUnsuspendUseCase.Args(ref_id))
