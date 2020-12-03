"""Command for showing the smart list item."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsItemShow(command.Command):
    """Command for showing the smart list items."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-item-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of smart list items"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the smart list items to show")
        parser.add_argument("--smart-list", dest="smart_list_keys", default=[], action="append",
                            help="Allow only smart list items from this smart list")
        parser.add_argument("--done", dest="show_done", default=False, action="store_const",
                            const=True, help="Show only smart list items which are done")
        parser.add_argument("--not-done", dest="show_not_done", default=False, action="store_const",
                            const=True, help="Show only smart list items which are not done")
        parser.add_argument("--tag", dest="filter_tags", default=[], action="append",
                            help="Allow only smart list items with this tag")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        smart_list_keys = [self._basic_validator.smart_list_key_validate_and_clean(key)
                           for key in args.smart_list_keys] \
            if len(args.smart_list_keys) > 0 else None
        filter_is_done = None
        if args.show_done and not args.show_not_done:
            filter_is_done = True
        elif not args.show_done and args.show_not_done:
            filter_is_done = False
        filter_tags = [self._basic_validator.tag_validate_and_clean(t) for t in args.filter_tags] \
            if len(args.filter_tags) > 0 else None

        response = self._smart_list_controller.load_all_smart_list_items(
            filter_ref_ids=ref_ids, filter_smart_list_keys=smart_list_keys, filter_is_done=filter_is_done,
            filter_tags=filter_tags)

        for smart_list_item_entry in response.smart_list_items:
            smart_list_item = smart_list_item_entry.smart_list_item
            smart_list = smart_list_item_entry.smart_list
            print(f'id={smart_list_item.ref_id} {smart_list_item.name}' +
                  (f' #done' if smart_list_item.is_done else '') +
                  ' '.join(f' #{tag}' for tag in smart_list_item.tags) +
                  (f' url={smart_list_item.url}' if smart_list_item.url else '') +
                  f' smart-list="{smart_list.name}"')
