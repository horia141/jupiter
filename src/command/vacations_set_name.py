"""Command for setting the name of a vacation."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.vacations as vacations
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSetName(command.Command):
    """Command class for setting the name of a vacation."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-set-name"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the name of a vacation"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("id", type=str, help="The id of the vacations to modify")
        parser.add_argument("name", type=str, help="The new name of the vacation")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        name = args.name

        # Load local storage

        the_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()

        workspace = workspace_repository.load_workspace()

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        vacation = vacations_repository.load_vacation_by_id(ref_id)
        vacation.set_name(name)
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
            vacation_row.title = vacation.name
            LOGGER.info("Applied Notion changes")
            break
        else:
            LOGGER.error("Did not find Notion task to remove")
