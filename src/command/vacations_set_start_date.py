import datetime
import logging
import pendulum

from notion.client import NotionClient

import command.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSetStartDate(command.Command):

    @staticmethod
    def name():
        return "vacations-set-start-date"

    @staticmethod
    def description():
        return "Change the start date of a vacation"

    def build_parser(self, parser):
        parser.add_argument("id", type=str, help="The id of the vacations to modify")
        parser.add_argument("start_date", type=str, help="The new start date of the vacation")

    def run(self, args):

        # Parse arguments

        ref_id = args.id
        start_date = pendulum.parse(args.start_date, tz="UTC")

        # Load local storage

        the_lock = lockfile.load_lock_file()
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Apply changes locally

        try:
            vacation = next(v for v in workspace["vacations"]["entries"] if v["ref_id"] == ref_id)
            if start_date >= pendulum.datetime(
                    vacation["end_date"].year, vacation["end_date"].month, vacation["end_date"].day):
                raise Exception("Cannot set a start date after the end date")
            vacation["start_date"] = datetime.date(start_date.year, start_date.month, start_date.day)
            storage.save_workspace(workspace)
            LOGGER.info("Modified vacation")
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
            vacation_row.start_date = vacation["start_date"]
            LOGGER.info("Applied Notion changes")
            break
        else:
            LOGGER.error("Did not find Notion task to remove")
