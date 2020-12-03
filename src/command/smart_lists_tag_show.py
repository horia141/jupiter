"""Command for showing the smart list tags."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsTagShow(command.Command):
    """Command for showing the smart list tags."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-tag-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of smart list tags"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the smart list tags to show")
        parser.add_argument("--smart-list", dest="smart_list_keys", default=[], action="append",
                            help="Allow only smart list items from this smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        smart_list_keys = [self._basic_validator.smart_list_key_validate_and_clean(key)
                           for key in args.smart_list_keys] \
            if len(args.smart_list_keys) > 0 else None
        response = self._smart_list_controller.load_all_smart_list_tag(
            filter_ref_ids=ref_ids, filter_smart_list_keys=smart_list_keys)

        for smart_list_tag_entry in response.smart_list_tags:
            smart_list_tag = smart_list_tag_entry.smart_list_tag
            smart_list = smart_list_tag_entry.smart_list
            print(f'id={smart_list_tag.ref_id} {smart_list_tag.name} smart-list="{smart_list.name}"')
