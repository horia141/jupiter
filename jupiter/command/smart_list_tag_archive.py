"""UseCase for archiving a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.use_cases.smart_lists.tag.archive import SmartListTagArchiveUseCase
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class SmartListTagArchive(command.Command):
    """UseCase for archiving a smart list tag."""

    _command: Final[SmartListTagArchiveUseCase]

    def __init__(self, the_command: SmartListTagArchiveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True, help="The id of the smart list tag")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(SmartListTagArchiveUseCase.Args(ref_id=ref_id))
