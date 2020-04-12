"""Command for setting the end date of a vacation."""

import datetime
import logging
import pendulum

from notion.client import NotionClient

import command.command as command
import service.vacations as vacations
import service.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSetEndDate(command.Command):
    """Command class for setting the end date of a vacation."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-set-end-date"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the end date of a vacation"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("id", type=str, help="The id of the vacations to modify")
        parser.add_argument("end_date", type=str, help="The new end date of the vacation")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        end_date = pendulum.parse(args.end_date, tz="UTC")

        # Load local storage

        the_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()

        workspace = workspace_repository.load_workspace()

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        vacation = vacations_repository.load_vacation_by_id(ref_id)
        if end_date <= pendulum.instance(vacation.start_date):
            raise Exception("Cannot set an end date before the start date")
        vacation.set_end_date(datetime.date(end_date.year, end_date.month, end_date.day))
        vacations_repository.save_vacation(vacation)
        LOGGER.info("Modified vacation")

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        vacations_rows = client \
            .get_collection_view(the_lock["vacations"]["database_view_id"], collection=vacations_page.collection) \
            .build_query() \
            .execute()

        for vacation_row in vacations_rows:
            if vacation_row.ref_id != ref_id:
                continue
            vacation_row.end_date = vacation.end_date
            LOGGER.info("Applied Notion changes")
            break
        else:
            LOGGER.error("Did not find Notion task to remove")
