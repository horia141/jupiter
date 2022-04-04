"""UseCase for hard removing a smart list tag."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.use_cases.smart_lists.tag.remove import SmartListTagRemoveUseCase
from jupiter.framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class SmartListTagRemove(command.Command):
    """UseCase for hard removing a smart list tag."""

    _command: Final[SmartListTagRemoveUseCase]

    def __init__(self, the_command: SmartListTagRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "smart-list-tag-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a smart list tag"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_ids",
            default=[],
            action="append",
            required=True,
            help="The id of the smart list tag to hard remove",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(SmartListTagRemoveUseCase.Args(ref_id=ref_id))
