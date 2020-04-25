"""Command for syncing the vacations from Notion."""

import logging
from typing import Dict

from notion.client import NotionClient
import pendulum

import command.command as command
from models.basic import EntityId, BasicValidator, SyncPrefer
import repository.vacations as vacations
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class VacationsSync(command.Command):
    """Command class for creating projects."""

    @staticmethod
    def name():
        """The name of the command."""
        return "vacations-sync"

    @staticmethod
    def description():
        """The description of the command."""
        return "Synchronises Notion and the local storage"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", dest="sync_prefer", choices=BasicValidator.sync_prefer_values(),
                            default=SyncPrefer.NOTION.value, help="Which source to prefer")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        sync_prefer = basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)

        # Load local storage

        the_lock = storage.load_lock_file()
        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()

        workspace = workspace_repository.load_workspace()

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # Apply changes locally

        all_vacations = vacations_repository.load_all_vacations()

        vacations_set: Dict[EntityId, vacations.Vacation] = {v.ref_id: v for v in all_vacations}

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
                if vacation_row.start_date.start >= vacation_row.end_date.start:
                    raise Exception(f"Start date for vacation {vacation_row.title} is after end date")

                new_vacation = vacations_repository.create_vacation(
                    archived=False,
                    name=vacation_row.title,
                    start_date=pendulum.instance(vacation_row.start_date.start),
                    end_date=pendulum.instance(vacation_row.end_date.start))
                LOGGER.info(f"Found new vacation from Notion {vacation_row.title}")

                vacation_row.ref_id = new_vacation.ref_id
                LOGGER.info(f"Applies changes on Notion side too as {vacation_row}")

                vacations_rows_set[vacation_row.ref_id] = vacation_row
            elif vacation_row.ref_id in vacations_set:
                # If the vacation exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if vacation_row.start_date.start >= vacation_row.end_date.start:
                        raise Exception(f"Start date for vacation {vacation_row.title} is after end date")
                    vacations_set[vacation_row.ref_id].name = vacation_row.title
                    vacations_set[vacation_row.ref_id].start_date = vacation_row.start_date.start
                    vacations_set[vacation_row.ref_id].end_date = vacation_row.end_date.start
                    vacations_repository.save_vacation(vacations_set[vacation_row.ref_id])
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    vacation_row.title = vacations_set[vacation_row.ref_id].name
                    vacation_row.start_date = vacations_set[vacation_row.ref_id].start_date
                    vacation_row.end_date = vacations_set[vacation_row.ref_id].end_date
                    LOGGER.info(f"Changed vacation with id={vacation_row.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
                vacations_rows_set[vacation_row.ref_id] = vacation_row
            else:
                # If the vacation is not new, and does not exist on the local side, it means it got removed
                # badly, and we need to redo this.
                vacation_row.archived = True
                LOGGER.info(f"Removed vacation with id={vacation_row.ref_id} from Notion")

        # Explore local and apply to Notion now
        for vacation in all_vacations:
            if vacation["ref_id"] in vacations_rows_set:
                # The vacation already exists on Notion side, so it was handled by the above loop!
                continue

            # If the vacation does not exist on Notion side, we create it.
            new_vacation_row = vacations_page.collection.add_row()
            new_vacation_row.title = vacation.name
            new_vacation_row.start_date = vacation.start_date
            new_vacation_row.end_date = vacation.end_date
            new_vacation_row.ref_id = vacation.ref_id
            LOGGER.info(f"Created new vacation on Notion side {new_vacation_row}")
