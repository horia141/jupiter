"""Command for creating a smart list tag."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsTagCreate(command.Command):
    """Command for creating a smart list tag."""

    _basic_validator: Final[BasicValidator]
    _smart_lists_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_lists_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-tag-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_key", required=True,
                            help="The key of the smart list to add the tag to")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = self._basic_validator.smart_list_key_validate_and_clean(args.smart_list_key)
        name = self._basic_validator.tag_validate_and_clean(args.name)
        self._smart_lists_controller.create_smart_list_tag(smart_list_key, name)
