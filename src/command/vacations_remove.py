import logging

from notion.client import NotionClient

import command.command as command
import lockfile
import space_utils
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
        parser.add_argument("id", type=str, help="The id of the vacations to remove")

    def run(self, args):

        # Parse arguments

        ref_id = args.id

        # Load local storage

        the_lock = lockfile.load_lock_file()
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Apply changes locally

        try:
            idx = next(i for i, v in enumerate(workspace["vacations"]["entries"]) if v["ref_id"] == ref_id)
            del workspace["vacations"]["entries"][idx]
            storage.save_workspace(workspace)
            LOGGER.info("Removed vacations")
        except StopIteration:
            LOGGER.error(f"Vacation with id {ref_id} does not exist")
            return

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        vacations_rows = client \
            .get_collection_view(the_lock["vacations"]["database_view_id"], collection=vacations_page.collection) \
            .build_query() \
            .execute()

        for vacation_row in vacations_rows:
            if vacation_row.ref_id != ref_id:
                continue
            vacation_row.remove()
            LOGGER.info("Applied Notion changes")
            break
        else:
            LOGGER.error("Did not find Notion task to remove")
