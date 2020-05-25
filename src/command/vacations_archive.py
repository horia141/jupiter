"""Command for removing a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.vacations import VacationsController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationsArchive(command.Command):
    """Command class for removing a vacation."""

    _basic_validator: Final[BasicValidator]
    _vacations_controller: Final[VacationsController]

    def __init__(self, basic_validator: BasicValidator, vacations_controller: VacationsController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._vacations_controller = vacations_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacations-archive"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Remove a vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the vacations to remove")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        self._vacations_controller.archive_vacation(ref_id)
