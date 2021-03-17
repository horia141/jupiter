"""Command for creating a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_item_create import SmartListItemCreateCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListItemCreate(command.Command):
    """Command for creating a smart list item."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListItemCreateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListItemCreateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_key", required=True,
                            help="The key of the smart list to add the item to")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list item")
        parser.add_argument("--done", dest="is_done", default=False, action="store_const", const=True,
                            help="Mark the smart list item as done")
        parser.add_argument("--tag", dest="tags", default=[], action="append",
                            help="Tags for the smart list item")
        parser.add_argument("--url", dest="url", help="An url for the smart list item")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = self._basic_validator.smart_list_key_validate_and_clean(args.smart_list_key)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        is_done = args.is_done
        tags = [self._basic_validator.tag_validate_and_clean(t) for t in args.tags]
        url = self._basic_validator.url_validate_and_clean(args.url) if args.url else None
        self._command.execute(SmartListItemCreateCommand.Args(
            smart_list_key=smart_list_key, name=name, is_done=is_done, tags=tags, url=url))
