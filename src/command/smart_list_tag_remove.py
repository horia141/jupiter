"""Command for hard removing a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from command import command
from domain.smart_lists.commands.smart_list_tag_remove import SmartListTagRemoveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListTagRemove(command.Command):
    """Command for hard removing a smart list tag."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListTagRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListTagRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="The id of the smart list tag to hard remove")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(ref_id)
