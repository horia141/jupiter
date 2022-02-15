"""UseCase for removing a chore."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.framework.base.entity_id import EntityId
from jupiter.use_cases.chores.archive import ChoreArchiveUseCase

LOGGER = logging.getLogger(__name__)


class ChoreArchive(command.Command):
    """UseCase class for removing a chore."""

    _command: Final[ChoreArchiveUseCase]

    def __init__(self, the_command: ChoreArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a chore"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(ChoreArchiveUseCase.Args(ref_id))
