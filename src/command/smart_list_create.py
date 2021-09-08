"""Command for creating a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.common.entity_name import EntityName
from domain.smart_lists.commands.smart_list_create import SmartListCreateCommand
from domain.smart_lists.smart_list_key import SmartListKey

LOGGER = logging.getLogger(__name__)


class SmartListCreate(command.Command):
    """Command for creating a smart list."""

    _command: Final[SmartListCreateCommand]

    def __init__(self, the_command: SmartListCreateCommand) -> None:
        """Constructor."""
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
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)
        name = EntityName.from_raw(args.name)
        self._command.execute(SmartListCreateCommand.Args(key=smart_list_key, name=name))
