"""Command for initialising a workspace"""

import logging

from notion.block import CollectionViewPageBlock
from notion.client import NotionClient

import command.command as command
import lockfile
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceInit(command.Command):

    @staticmethod
    def name():
        return "ws-init"

    @staticmethod
    def description():
        return "Initialise a workspace"

    def build_parser(self, parser):
        parser.add_argument("--name", required=True, help="The plan name to use")
        parser.add_argument("--token", dest="token", required=True, help="The Notion access token to use")
        parser.add_argument("--space-id", dest="space_id", required=True, help="The Notion space id to use")

    def run(self, args):

        # Arguments parsing

        name = args.name
        token = args.token
        space_id = args.space_id

        # Load local storage

        try:
            system_lock = lockfile.load_lock_file()
            LOGGER.info("Found system lock")
        except Exception as e:
            system_lock = lockfile.build_empty_lockfile()
            LOGGER.info("No system lock - creating it")

        try:
            workspace = storage.load_workspace()
            LOGGER.info("Found workspace config")
        except IOError as e:
            workspace = storage.build_empty_workspace()
            LOGGER.info("No workspace config - creating it")

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=token)
        space = client.get_space(space_id)

        # Apply the changes to the Notion side

        (root_page_lock, root_page) = self.update_root_page(client, space, system_lock.get("root_page", {}), name)
        vacations_lock = self.update_vacations(client, root_page, system_lock.get("vacations", {}))

        # Apply the changes to the local side

        workspace["space_id"] = space_id
        workspace["name"] = name
        workspace["token"] = token
        storage.save_workspace(workspace)
        LOGGER.info("Applied changes on local workspace")

        # Save changes to lockfile
        system_lock["root_page"] = root_page_lock
        system_lock["vacations"] = vacations_lock
        lockfile.save_lock_file(system_lock)
        LOGGER.info("Applied changes on lockfile")

    def update_root_page(self, client, space, lock, name):
        if "root_page_id" in lock:
            found_root_page = space_utils.find_page_from_space_by_id(client, lock["root_page_id"])
            LOGGER.info(f"Found the root page via id {found_root_page}")
        else:
            LOGGER.info("Attempting to find root page via name in full space")
            found_root_page = space_utils.find_page_from_space_by_name(client, name, space)
            LOGGER.info(f"Found the root page via name {found_root_page}")
        if not found_root_page:
            found_root_page = space_utils.create_page_in_space(space, name)
            LOGGER.info(f"Created the root page {found_root_page}")

        found_root_page.title = name
        LOGGER.info("Applied changes to root page on Notion side")

        return ({
                    "root_page_id": found_root_page.id
                }, found_root_page)

    def update_vacations(self, client, root_page, lock):
        if "root_page_id" in lock:
            vacations_page = space_utils.find_page_from_space_by_id(client, lock["root_page_id"])
            LOGGER.info(f"Found the vacation page via id {vacations_page}")
        else:
            LOGGER.info("Attempting to find vacation page via name")
            vacations_page = space_utils.find_page_from_page_by_name(root_page, "Vacations")
            LOGGER.info(f"Found the vacation page via name {vacations_page}")
        if not vacations_page:
            vacations_page = root_page.children.add_new(CollectionViewPageBlock)
            LOGGER.info(f"Created the vacation page {vacations_page}")

        lock["root_page_id"] = vacations_page.id

        vacations_schema = schema.get_vacations_schema()

        vacations_collection_id = vacations_page.get("collection_id")
        if vacations_collection_id:
            vacations_collection = client.get_collection(vacations_collection_id)
            LOGGER.info(f"Found the already existing inbox page collection via id {vacations_collection}")
            vacations_old_schema = vacations_collection.get("schema")
            vacations_schema = self.merge_schemas(vacations_old_schema, vacations_schema)
            vacations_collection.set("schema", vacations_schema)
        else:
            vacations_collection = client.get_collection(
                client.create_record("collection", parent=vacations_page, schema=vacations_schema))
            inbox_collection_id = vacations_collection.id
            LOGGER.info(f"Created the inbox page collection as {vacations_collection}")

        vacations_collection.name = "Vacations"

        vacations_collection_database_view = space_utils.attach_view_to_collection(
            client, vacations_page, vacations_collection, lock.get("database_view_id"), "table",
            "Database", schema.VACATIONS_DATABASE_VIEW_SCHEMA)
        lock["database_view_id"] = vacations_collection_database_view.id

        vacations_page.set("collection_id", vacations_collection.id)
        vacations_page.set("view_ids", [ vacations_collection_database_view.id ])

        return lock

    def merge_schemas(self, old_schema, new_schema):
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        for (k, v) in new_schema.items():
            if v["type"] == "select" or v["type"] == "multi_select":
                if k in old_schema:
                    old_v = old_schema[k]

                    combined_schema[k] = {
                        "name": v["name"],
                        "type": v["type"],
                        "options": []
                    }

                    for option in v["options"]:
                        old_option = next((old_o for old_o in old_v["options"] if old_o["value"] == option["value"]),
                                          None)
                        if old_option is not None:
                            combined_schema[k]["options"].append({
                                "color": option["color"],
                                "value": option["value"],
                                "id": old_option["id"]
                            })
                        else:
                            combined_schema[k]["options"].append(option)
                else:
                    combined_schema[k] = v
            else:
                combined_schema[k] = v

        return combined_schema
