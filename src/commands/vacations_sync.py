import datetime
import logging

import pendulum
from notion.client import NotionClient

import commands.command as command
import lockfile
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSync(command.Command):

    @staticmethod
    def name():
        return "vacations-sync"

    @staticmethod
    def description():
        return "Synchronises Notion and the local storage"

    def build_parser(self, parser):
        parser.add_argument("--prefer", choices=["notion", "local"], default="notion", help="Which source to prefer")

    def run(self, args):

        # Parse arguments

        prefer = args.prefer

        # Load local storage

        the_lock = lockfile.load_lock_file()
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Apply changes locally

        vacations_set = {v["ref_id"]: v for v in workspace["vacations"]["entries"]}

        vacations_page = space_utils.find_page_from_space_by_id(client, the_lock["vacations"]["root_page_id"])
        vacations_rows = client \
            .get_collection_view(the_lock["vacations"]["database_view_id"], collection=vacations_page.collection) \
            .build_query() \
            .execute()

        # Explore Notion and apply to local
        vacations_rows_set = {}
        for vacation_row in vacations_rows:
            LOGGER.info(f"Processing {vacation_row}")
            if vacation_row.ref_id is None or vacation_row.ref_id == "":
                # If the vacation doesn't exist locally, we create it:
                new_vacation = {
                    "ref_id": str(workspace["vacations"]["next_idx"]),
                    "name": vacation_row.title,
                    "start_date": vacation_row.start_date.start,
                    "end_date": vacation_row.end_date.start
                }
                if vacation_row.start_date.start >= vacation_row.end_date.start:
                    raise Exception(f"Start date for vacation {vacation_row.title} is after end date")
                workspace["vacations"]["next_idx"] = workspace["vacations"]["next_idx"] + 1
                workspace["vacations"]["entries"].append(new_vacation)
                LOGGER.info(f"Found new vacation from Notion {vacation_row.title}")
                vacation_row.ref_id = new_vacation["ref_id"]
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")
                vacations_rows_set[vacation_row.ref_id] = vacation_row
            elif vacation_row.ref_id in vacations_set:
                # If the vacation exists locally, we sync it with the remote:
                if prefer == "notion":
                    vacations_set[vacation_row.ref_id]["name"] = vacation_row.title
                    vacations_set[vacation_row.ref_id]["start_date"] = vacation_row.start_date.start
                    vacations_set[vacation_row.ref_id]["end_date"] = vacation_row.end_date.start
                    if vacation_row.start_date.start >= vacation_row.end_date.start:
                        raise Exception(f"Start date for vacation {vacation_row.title} is after end date")
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from Notion")
                elif prefer == "local":
                    vacation_row.title = vacations_set[vacation_row.ref_id]["name"]
                    vacation_row.start_date = vacations_set[vacation_row.ref_id]["start_date"]
                    vacation_row.end_date = vacations_set[vacation_row.ref_id]["end_date"]
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {prefer}")
                vacations_rows_set[vacation_row.ref_id] = vacation_row
            else:
                # If the vacation is not new, and does not exist on the local side, it means it got removed
                # badly, and we need to redo this.
                vacation_row.remove()
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in workspace["vacations"]["entries"]:
            if vacation["ref_id"] in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue

            # If the vacation does not exist on Notion side, we create it.
            new_vacation_row = vacations_page.collection.add_row()
            new_vacation_row.title = vacation["name"]
            new_vacation_row.start_date = vacation["start_date"]
            new_vacation_row.end_date = vacation["end_date"]
            new_vacation_row.ref_id = vacation["ref_id"]
            LOGGER.info(f"Created new vacation on Notion side {new_vacation_row}")

        workspace["vacations"]["entries"] = sorted(
            workspace["vacations"]["entries"], key=lambda vac: vac["start_date"])
        storage.save_workspace(workspace)
        LOGGER.info("Applied local changes")
