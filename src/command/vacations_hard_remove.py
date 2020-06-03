"""Command for hard remove vacations."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.vacations import VacationsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationsHardRemove(command.Command):
    """Command class for hard removing vacations."""

    _basic_validator: Final[BasicValidator]
    _vacations_controller: Final[VacationsController]

    def __init__(self, basic_validator: BasicValidator, vacations_controller: VacationsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._vacations_controller = vacations_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacations-hard-remove"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Hard remove vacations"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            required=True, help="Show only tasks selected by this id")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        # Parse arguments
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids]
        self._vacations_controller.hard_remove_vacations(ref_ids)
