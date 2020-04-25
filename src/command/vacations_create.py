"""Command for adding a vacation."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.vacations as vacations
import repository.workspaces as workspaces
import space_utils
import storage
from models.basic import BasicValidator

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
        basic_validator = BasicValidator()

        # Parse arguments

        name = basic_validator.entity_name_validate_and_clean(args.name)
        start_date = basic_validator.datetime_validate_and_clean(args.start_date)
        end_date = basic_validator.datetime_validate_and_clean(args.end_date)

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
            start_date=start_date,
            end_date=end_date)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        new_vacation_row = vacations_page.collection.add_row()
        new_vacation_row.title = name
        new_vacation_row.start_date = new_vacation.start_date
        new_vacation_row.end_date = new_vacation.end_date
        new_vacation_row.ref_id = new_vacation.ref_id
        LOGGER.info("Applied Notion changes")
