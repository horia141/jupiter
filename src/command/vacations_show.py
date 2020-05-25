"""Command for showing the vacations."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.vacations import VacationsController

LOGGER = logging.getLogger(__name__)


class VacationsShow(command.Command):
    """Command class for showing the vacations."""

    _vacations_controller: Final[VacationsController]

    def __init__(self, vacations_controller: VacationsController):
        """Constructor."""
        self._vacations_controller = vacations_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "vacations-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the list of vacations"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--show-archived", dest="show_archived", default=False, action="store_true",
                            help="Whether to show archived vacations or not")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        for vacation in self._vacations_controller.load_all_vacations(show_archived):
            print(f'id={vacation.ref_id} {vacation.name} start={vacation.start_date} end={vacation.end_date} ' +
                  f'{"archived=" + str(vacation.archived) if show_archived else ""}')
