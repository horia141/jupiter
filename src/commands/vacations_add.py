import datetime
import logging

import pendulum
from notion.client import NotionClient

import commands.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsAdd(command.Command):

    @staticmethod
    def name():
        return "vacations-add"

    @staticmethod
    def description():
        return "Add a new vacation"

    def build_parser(self, parser):
        parser.add_argument("--start-date", dest="start_date", required=True, help="The plan name to use")
        parser.add_argument("--end-date", dest="end_date",required=True, help="The Notion access token to use")

    def run(self, args):

        # Parse arguments

        start_date = pendulum.parse(args.start_date, tz="UTC")
        end_date = pendulum.parse(args.end_date, tz="UTC")

        if start_date >= end_date:
            raise Exception(f"Start date {start_date} is after {end_date}")

        # Load local storage

        the_lock = lockfile.load_lock_file()
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Apply changes locally

        new_vacation = {
            "start_date": datetime.date(start_date.year, start_date.month, start_date.day),
            "end_date": datetime.date(end_date.year, end_date.month, end_date.day)
        }
        workspace["vacations"].append(new_vacation)
        workspace["vacations"] = sorted(workspace["vacations"], key=lambda vac: vac["start_date"])
        storage.save_workspace(workspace)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        new_vacation_row = vacations_page.collection.add_row()
        new_vacation_row.title = "New vacation"
        new_vacation_row.start_date = new_vacation["start_date"]
        new_vacation_row.end_date = new_vacation["end_date"]
        LOGGER.info("Applied Notion changes")
