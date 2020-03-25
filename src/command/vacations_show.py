"""Command for showing the vacations."""

import logging

import command.command as command
import storage

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
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Dump out contents of the vacations

        for vacation in workspace["vacations"]["entries"]:
            print(
                f'id={vacation["ref_id"]} {vacation["name"]} start={vacation["start_date"]} end={vacation["end_date"]}')
