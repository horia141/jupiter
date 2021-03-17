"""Command for archiving a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_tag_archive import SmartListTagArchiveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListTagArchive(command.Command):
    """Command for archiving a smart list tag."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListTagArchiveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListTagArchiveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
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
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        self._command.execute(ref_id)
