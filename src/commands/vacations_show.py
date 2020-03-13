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

        for vacation in workspace["vacations"]["entries"]:
            print(f'id={vacation["ref_id"]} {vacation["name"]} start={vacation["start_date"]} end={vacation["end_date"]}')
