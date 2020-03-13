import logging
import sys

import yaml

import commands.command as command
import storage

LOGGER = logging.getLogger(__name__)


class VacationsShow(command.Command):

    @staticmethod
    def name():
        return "vacations-show"

    @staticmethod
    def description():
        return "Show the list of vacations"

    def build_parser(self, parser):
        pass

    def run(self, args):

        # Load local storage

        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Dump out contents of workspace

        yaml.safe_dump(workspace["vacations"], sys.stdout)
