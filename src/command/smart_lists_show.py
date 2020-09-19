"""Command for showing a smart list."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsShow(command.Command):
    """Command for showing the smart list."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of smart lists"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the smart list to show")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        response = self._smart_list_controller.load_all_smart_lists(filter_ref_ids=ref_ids)

        for smart_list_entry in response.smart_lists:
            smart_list = smart_list_entry.smart_list
            print(f'id={smart_list.ref_id} {smart_list.name}:')

            for smart_list_item in smart_list_entry.smart_list_items:
                print(f'  - id={smart_list_item.ref_id} {smart_list_item.name}' +
                      (f' url={smart_list_item.url}' if smart_list_item.url else ''))
