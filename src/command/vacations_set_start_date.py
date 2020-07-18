"""Command for setting the start date of a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.vacations import VacationsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationsSetStartDate(command.Command):
    """Command class for setting the start data of a vacation."""

    _basic_validator: Final[BasicValidator]
    _vacations_controller: Final[VacationsController]

    def __init__(self, basic_validator: BasicValidator, vacations_controller: VacationsController):
        """Constructor."""
        self._basic_validator = basic_validator
        self._vacations_controller = vacations_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacations-set-start-date"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the start date of a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--start-date", type=str, dest="start_date", required=True,
                            help="The new start date of the vacation")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        start_date = self._basic_validator.adate_validate_and_clean(args.start_date)

        self._vacations_controller.set_vacation_start_date(ref_id, start_date)
