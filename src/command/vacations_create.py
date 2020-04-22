"""Command for adding a vacation."""

import datetime
import logging

import pendulum
from notion.client import NotionClient

import command.command as command
import repository.vacations as vacations
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsCreate(command.Command):
    """Command class for adding a vacation."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Add a new vacation"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", dest="name", required=True, help="The name of the vacation")
        parser.add_argument("--start-date", dest="start_date", required=True, help="The vacation start date")
        parser.add_argument("--end-date", dest="end_date", required=True, help="The vacation end date")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        name = args.name
        start_date = pendulum.parse(args.start_date, tz="UTC")
        end_date = pendulum.parse(args.end_date, tz="UTC")

        if start_date >= end_date:
            raise Exception(f"Start date {start_date} is after {end_date}")

        # Load local storage

        the_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()
        workspace = workspace_repository.load_workspace()

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        new_vacation = vacations_repository.create_vacation(
            archived=False,
            name=name,
            start_date=datetime.date(start_date.year, start_date.month, start_date.day),
            end_date=datetime.date(end_date.year, end_date.month, end_date.day))
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        new_vacation_row = vacations_page.collection.add_row()
        new_vacation_row.title = name
        new_vacation_row.start_date = new_vacation.start_date
        new_vacation_row.end_date = new_vacation.end_date
        new_vacation_row.ref_id = new_vacation.ref_id
        LOGGER.info("Applied Notion changes")
