"""Command for archiving a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from use_cases.smart_lists.item.archive import SmartListItemArchiveCommand
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class SmartListItemArchive(command.Command):
    """Command for archiving of a smart list item."""

    _command: Final[SmartListItemArchiveCommand]

    def __init__(self, the_command: SmartListItemArchiveCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True,
                            help="The id of the smart list item to archive")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        self._command.execute(ref_id)
