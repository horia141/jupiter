"""Command for setting the start date of a vacation."""

import logging
import pendulum

from notion.client import NotionClient

import command.command as command
import service.vacations as vacations
import service.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSetStartDate(command.Command):
    """Command class for setting the start data of a vacation."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-set-start-date"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the start date of a vacation"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("id", type=str, help="The id of the vacations to modify")
        parser.add_argument("start_date", type=str, help="The new start date of the vacation")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        start_date = pendulum.parse(args.start_date, tz="UTC")

        # Load local storage

        the_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()

        workspace = workspace_repository.load_workspace()

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        vacation = vacations_repository.load_vacation_by_id(ref_id)
        if start_date >= pendulum.instance(vacation.end_date):
            raise Exception("Cannot set a start date after the end date")
        vacation.set_start_date(start_date)
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
            vacation_row.start_date = vacation.start_date
            LOGGER.info("Applied Notion changes")
            break
        else:
            LOGGER.error("Did not find Notion task to remove")
