"""Command for archiving a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_archive import SmartListArchiveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListArchive(command.Command):
    """Command for archiving of a smart list."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListArchiveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListArchiveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Archive a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_key", required=True,
                            help="The key of the smart list to archive")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = self._basic_validator.smart_list_key_validate_and_clean(args.smart_list_key)
        self._command.execute(smart_list_key)
