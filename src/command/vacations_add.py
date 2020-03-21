"""Command for adding a vacation"""

import datetime
import logging

import pendulum
from notion.client import NotionClient

import command.command as command
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
        parser.add_argument("--name", dest="name", required=True, help="The name of the vacation")
        parser.add_argument("--start-date", dest="start_date", required=True, help="The vacation start date")
        parser.add_argument("--end-date", dest="end_date",required=True, help="The vacation end date")

    def run(self, args):

        # Parse arguments

        name = args.name
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
            "ref_id": str(workspace["vacations"]["next_idx"]),
            "name": name,
            "start_date": datetime.date(start_date.year, start_date.month, start_date.day),
            "end_date": datetime.date(end_date.year, end_date.month, end_date.day)
        }
        workspace["vacations"]["next_idx"] = workspace["vacations"]["next_idx"] + 1
        workspace["vacations"]["entries"].append(new_vacation)
        workspace["vacations"]["entries"] = sorted(workspace["vacations"]["entries"], key=lambda vac: vac["start_date"])
        storage.save_workspace(workspace)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        new_vacation_row = vacations_page.collection.add_row()
        new_vacation_row.title = name
        new_vacation_row.start_date = new_vacation["start_date"]
        new_vacation_row.end_date = new_vacation["end_date"]
        new_vacation_row.ref_id = new_vacation["ref_id"]
        LOGGER.info("Applied Notion changes")
