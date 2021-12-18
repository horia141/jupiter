"""Command for updating a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from domain.entity_name import EntityName
from domain.smart_lists.smart_list_key import SmartListKey
from models.framework import UpdateAction
from use_cases.smart_lists.update import SmartListUpdateCommand

LOGGER = logging.getLogger(__name__)


class SmartListUpdate(command.Command):
    """Command for updating a smart list."""

    _command: Final[SmartListUpdateCommand]

    def __init__(self, the_command: SmartListUpdateCommand) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a new smart list"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--smart-list", dest="smart_list_key", required=True, help="The key of the smart list")
        parser.add_argument("--name", dest="name", required=True, help="The name of the smart list")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        smart_list_key = SmartListKey.from_raw(args.smart_list_key)
        if args.name:
            name = UpdateAction.change_to(EntityName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        self._command.execute(SmartListUpdateCommand.Args(key=smart_list_key, name=name))
