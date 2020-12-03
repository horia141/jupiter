"""Command for changing the name of a smart list item."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsItemSetName(command.Command):
    """Command for changing the name of a smart list item."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-item-set-name"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the name of a smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True,
                            help="The id of the smart list item to change the name of")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list item")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        self._smart_list_controller.set_smart_list_item_name(ref_id, name)
