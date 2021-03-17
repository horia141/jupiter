"""Command for showing a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_find import SmartListFindCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListShow(command.Command):
    """Command for showing the smart list."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListFindCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListFindCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of smart lists"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--show-archived", dest="show_archived", default=False, action="store_true",
                            help="Whether to show archived vacations or not")
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
        show_archived = args.show_archived
        keys = [self._basic_validator.smart_list_key_validate_and_clean(rid) for rid in args.smart_list_keys] \
            if len(args.smart_list_keys) > 0 else None
        filter_is_done = None
        if args.show_done and not args.show_not_done:
            filter_is_done = True
        elif not args.show_done and args.show_not_done:
            filter_is_done = False
        filter_tags = [self._basic_validator.tag_validate_and_clean(t) for t in args.filter_tags] \
            if len(args.filter_tags) > 0 else None
        response = self._command.execute(SmartListFindCommand.Args(
            allow_archived=show_archived, filter_keys=keys, filter_is_done=filter_is_done, filter_tags=filter_tags))

        for smart_list_entry in response.smart_lists:
            smart_list = smart_list_entry.smart_list
            smart_list_tags_set = {t.ref_id: t for t in smart_list_entry.smart_list_tags}
            print(f'{smart_list.key}: {smart_list.name}')

            for smart_list_item in smart_list_entry.smart_list_items:
                print(f'  - id={smart_list_item.ref_id} {smart_list_item.name}' +
                      (' [x] ' if smart_list_item.is_done else ' [ ] ') +
                      (' '.join(f'#{smart_list_tags_set[t].name}' for t in smart_list_item.tags)) +
                      (f' url={smart_list_item.url}' if smart_list_item.url else '') +
                      f'{"archived=" + str(smart_list_item.archived) if show_archived else ""}')
