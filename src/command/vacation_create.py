"""Command for adding a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from domain.vacations.commands.vacation_create import VacationCreateCommand
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class VacationCreate(command.Command):
    """Command class for adding a vacation."""

    _basic_validator: Final[BasicValidator]
    _command: Final[VacationCreateCommand]

    def __init__(self, basic_validator: BasicValidator, the_command: VacationCreateCommand):
        """Constructor."""
        self._basic_validator = basic_validator
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacation-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Add a new vacation"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", dest="name", required=True, help="The name of the vacation")
        parser.add_argument("--start-date", dest="start_date", required=True, help="The vacation start date")
        parser.add_argument("--end-date", dest="end_date", required=True, help="The vacation end date")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        start_date = self._basic_validator.adate_validate_and_clean(args.start_date)
        end_date = self._basic_validator.adate_validate_and_clean(args.end_date)

        self._command.execute(VacationCreateCommand.Args(
            name=name, start_date=start_date, end_date=end_date))
