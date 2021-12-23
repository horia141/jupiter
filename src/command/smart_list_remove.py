"""UseCase for hard removing a smart list."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from use_cases.smart_lists.remove import SmartListRemoveUseCase
from domain.smart_lists.smart_list_key import SmartListKey

LOGGER = logging.getLogger(__name__)


class SmartListsRemove(command.Command):
    """UseCase for hard removing of a smart list."""

    _command: Final[SmartListRemoveUseCase]

    def __init__(self, the_command: SmartListRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-remove"

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
        smart_list_keys = [SmartListKey.from_raw(srk) for srk in args.smart_list_keys]
        for key in smart_list_keys:
            self._command.execute(key)
