"""Command for showing the workspace"""

import logging

import command.command as command
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceShow(command.Command):
    """Command class for showing the workspace"""

    @staticmethod
    def name():
        return "ws-show"

    @staticmethod
    def description():
        return "Show the current information about the workspace"

    def build_parser(self, parser):
        pass

    def run(self, args):
        # Load local storage

        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Dump out contents of workspace

        print(f'{workspace["name"]}:')

        print("  Vacations:")

        for vacation in workspace["vacations"]["entries"]:
            print(f'    id={vacation["ref_id"]} {vacation["name"]} ' +
                  f'start={vacation["start_date"]} end={vacation["end_date"]}')
