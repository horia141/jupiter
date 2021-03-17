"""Command for creating a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.smart_lists.commands.smart_list_create import SmartListCreateCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class SmartListCreate(command.Command):
    """Command for creating a smart list."""

    _basic_validator: Final[BasicValidator]
    _command: Final[SmartListCreateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: SmartListCreateCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_key", required=True, help="The key of the smart list")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = self._basic_validator.smart_list_key_validate_and_clean(args.smart_list_key)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        self._command.execute(SmartListCreateCommand.Args(key=smart_list_key, name=name))
