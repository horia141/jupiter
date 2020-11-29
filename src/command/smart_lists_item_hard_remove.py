"""Command for hard removing a smart list item."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsItemHardRemove(command.Command):
    """Command for hard removing of a smart list item."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-item-hard-remove"

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
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]
        self._smart_list_controller.hard_remove_smart_list_item(ref_ids)
