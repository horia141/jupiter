"""Command for hard remove vacations."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.vacations.commands.vacation_remove import VacationRemoveCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationRemove(command.Command):
    """Command class for hard removing vacations."""

    _basic_validator: Final[BasicValidator]
    _command: Final[VacationRemoveCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: VacationRemoveCommand) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
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
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]
        for ref_id in ref_ids:
            self._command.execute(ref_id)
