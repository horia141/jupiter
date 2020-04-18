"""Command for showing the vacations."""

import logging

import command.command as command
import repository.vacations as vacations

LOGGER = logging.getLogger(__name__)


class VacationsShow(command.Command):
    """Command class for showing the vacations."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the list of vacations"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""

    def run(self, args):
        """Callback to execute when the command is invoked."""
        vacations_repository = vacations.VacationsRepository()

        # Dump out contents of the vacations

        for vacation in vacations_repository.load_all_vacations():
            print(f'id={vacation.ref_id} {vacation.name} start={vacation.start_date} end={vacation.end_date}')
