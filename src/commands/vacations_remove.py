import logging

import commands.command as command
import storage

LOGGER = logging.getLogger(__name__)


class VacationsRemove(command.Command):

    @staticmethod
    def name():
        return "vacations-remove"

    @staticmethod
    def description():
        return "Remove a vacation"

    def build_parser(self, parser):
        parser.add_argument("id", type=int, help="The id of the vacations to remove")

    def run(self, args):

        # Parse arguments

        index = args.id

        if index < 0:
            raise Exception("Index is negative")

        # Load local storage

        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Apply changes

        if index >= len(workspace["vacations"]):
            raise Exception("Index is out of bounds")

        del workspace["vacations"][index]
        LOGGER.info("Removed vacations")

        # Save changes
        storage.save_workspace(workspace)
        LOGGER.info("Saved workspace data")
