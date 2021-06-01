"""Command for updating a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

import command.command as command
from domain.smart_lists.commands.smart_list_item_update import SmartListItemUpdateCommand
from models.basic import BasicValidator
from models.framework import UpdateAction, EntityId

LOGGER = logging.getLogger(__name__)


class SmartListItemUpdate(command.Command):
    """Command for updating a smart list item."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListItemUpdateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListItemUpdateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required=True,
                            help="The smart list item to update")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list item")
        parser.add_argument("--done", dest="is_done", default=False, action="store_const", const=True,
                            help="Mark the smart list item as done")
        parser.add_argument("--not-done", dest="is_not_done", default=False, action="store_const", const=True,
                            help="Mark the smart list item as not done")
        parser.add_argument("--tag", dest="tags", default=[], action="append",
                            help="Tags for the smart list item")
        parser.add_argument("--url", dest="url", help="An url for the smart list item")
        parser.add_argument("--clear-url", dest="clear_url", default=False,
                            action="store_const", const=True, help="Clear the url")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(self._basic_validator.entity_name_validate_and_clean(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.is_done:
            is_done = UpdateAction.change_to(True)
        elif args.is_not_done:
            is_done = UpdateAction.change_to(False)
        else:
            is_done = UpdateAction.do_nothing()
        if len(args.tags) > 0:
            tags = UpdateAction.change_to([self._basic_validator.tag_validate_and_clean(t) for t in args.tags])
        else:
            tags = UpdateAction.do_nothing()
        url: UpdateAction[Optional[str]]
        if args.clear_url:
            url = UpdateAction.change_to(None)
        elif args.url:
            url = UpdateAction.change_to(self._basic_validator.url_validate_and_clean(args.url))
        else:
            url = UpdateAction.do_nothing()
        self._command.execute(SmartListItemUpdateCommand.Args(
            ref_id=ref_id, name=name, tags=tags, is_done=is_done, url=url))
