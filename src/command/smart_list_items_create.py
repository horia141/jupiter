"""Command for creating a smart list item."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_list_items import SmartListItemsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListItemsCreate(command.Command):
    """Command for creating a smart list item."""

    _basic_validator: Final[BasicValidator]
    _smart_list_items_controller: Final[SmartListItemsController]

    def __init__(self, basic_validator: BasicValidator, smart_list_items_controller: SmartListItemsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_items_controller = smart_list_items_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-items-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_ref_id", required=True,
                            help="The id of the smart list to add this item to")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list item")
        parser.add_argument("--url", dest="url", help="An url for the smart list item")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_ref_id = self._basic_validator.entity_id_validate_and_clean(args.smart_list_ref_id)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        url = self._basic_validator.url_validate_and_clean(args.url) if args.url else None
        self._smart_list_items_controller.create_smart_list_item(
            smart_list_ref_id=smart_list_ref_id, name=name, url=url)
