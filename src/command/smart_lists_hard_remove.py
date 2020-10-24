"""Command for hard removing a smart list."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.smart_lists import SmartListsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListsHardRemove(command.Command):
    """Command for hard removing of a smart list."""

    _basic_validator: Final[BasicValidator]
    _smart_list_controller: Final[SmartListsController]

    def __init__(self, basic_validator: BasicValidator, smart_lists_controller: SmartListsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_list_controller = smart_lists_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-lists-hard-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_keys", required=True, default=[], action="append",
                            help="The key of the smart list to archive")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_keys = [self._basic_validator.smart_list_key_validate_and_clean(srk) for srk in args.smart_list_keys]
        self._smart_list_controller.hard_remove_smart_list(smart_list_keys)
