"""Command for hard removing a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_item_remove import SmartListItemRemoveCommand
from models.basic import BasicValidator
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class SmartListItemRemove(command.Command):
    """Command for hard removing of a smart list item."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListItemRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListItemRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="The if of the smart list item to hard remove")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(ref_id)
