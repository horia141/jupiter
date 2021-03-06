"""Command for archiving a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_item_archive import SmartListItemArchiveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListItemArchive(command.Command):
    """Command for archiving of a smart list item."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListItemArchiveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListItemArchiveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
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
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        self._command.execute(ref_id)
