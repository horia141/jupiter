"""UseCase for hard removing a smart list item."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from use_cases.smart_lists.item.remove import SmartListItemRemoveUseCase
from framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class SmartListItemRemove(command.Command):
    """UseCase for hard removing of a smart list item."""

    _command: Final[SmartListItemRemoveUseCase]

    def __init__(self, the_command: SmartListItemRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-item-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove a smart list item"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="The if of the smart list item to hard remove")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(ref_id)
