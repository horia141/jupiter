"""Command for setting the end date of a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.vacations import VacationsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationsSetEndDate(command.Command):
    """Command class for setting the end date of a vacation."""

    _basic_validator: Final[BasicValidator]
    _vacations_controller: Final[VacationsController]

    def __init__(self, basic_validator: BasicValidator, vacations_controller: VacationsController):
        """Constructor."""
        self._basic_validator = basic_validator
        self._vacations_controller = vacations_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacations-set-end-date"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the end date of a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacation to modify")
        parser.add_argument("--end-date", type=str, dest="end_date", required=True,
                            help="The new end date of the vacation")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        end_date = self._basic_validator.datetime_validate_and_clean(args.end_date)

        self._vacations_controller.set_vacation_end_date(ref_id, end_date)
