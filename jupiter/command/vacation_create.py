"""UseCase for adding a vacation."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import jupiter.command.command as command
from jupiter.domain.adate import ADate
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.use_cases.vacations.create import VacationCreateUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class VacationCreate(command.Command):
    """UseCase class for adding a vacation."""

    _global_properties: Final[GlobalProperties]
    _command: Final[VacationCreateUseCase]

    def __init__(self, global_properties: GlobalProperties, the_command: VacationCreateUseCase):
        """Constructor."""
        self._global_properties = global_properties
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
        name = VacationName.from_raw(args.name)
        start_date = ADate.from_raw(self._global_properties.timezone, args.start_date)
        end_date = ADate.from_raw(self._global_properties.timezone, args.end_date)

        self._command.execute(VacationCreateUseCase.Args(
            name=name, start_date=start_date, end_date=end_date))
