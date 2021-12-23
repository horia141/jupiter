"""UseCase for hard remove vacations."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from use_cases.vacations.remove import VacationRemoveUseCase
from framework.base.entity_id import EntityId

LOGGER = logging.getLogger(__name__)


class VacationRemove(command.Command):
    """UseCase class for hard removing vacations."""

    _command: Final[VacationRemoveUseCase]

    def __init__(self, the_command: VacationRemoveUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [EntityId.from_raw(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(ref_id)
