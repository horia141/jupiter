"""Command for initialising a workspace."""

import logging

from notion.block import CollectionViewPageBlock
from notion.client import NotionClient

import command.command as command
import repository.projects as projects
import repository.vacations as vacations
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class WorkspaceInit(command.Command):
    """Command class for initialising a workspace."""

    @staticmethod
    def name():
        """The name of the command."""
        return "ws-init"

    @staticmethod
    def description():
        """The description of the command."""
        return "Initialise a workspace"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", required=True, help="The plan name to use")
        parser.add_argument("--token", dest="token", required=True, help="The Notion access token to use")
        parser.add_argument("--space-id", dest="space_id", required=True, help="The Notion space id to use")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        name = args.name
        token = args.token
        space_id = args.space_id

        # Load local storage

        try:
            system_lock = storage.load_lock_file()
            LOGGER.info("Found system lock")
        except IOError:
            system_lock = storage.build_empty_lockfile()
            LOGGER.info("No system lock - creating it")

        workspace_repository = workspaces.WorkspaceRepository()
        vacations_repository = vacations.VacationsRepository()
        projects_repository = projects.ProjectsRepository()

        workspace_repository.initialize()
        vacations_repository.initialize()
        projects_repository.initialize()

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=token)
        space = client.get_space(space_id)

        # Apply the changes to the Notion side

        (root_page_lock, root_page) = self._update_root_page(client, space, system_lock.get("root_page", {}), name)
        vacations_lock = self._update_vacations(client, root_page, system_lock.get("vacations", {}))

        # Apply the changes to the local side

        new_workspace = workspaces.Workspace(
            name, workspaces.WorkspaceSpaceId(space_id), workspaces.WorkspaceToken(token))
        workspace_repository.save_workspace(new_workspace)

        # Save changes to lockfile
        system_lock["root_page"] = root_page_lock
        system_lock["vacations"] = vacations_lock
        storage.save_lock_file(system_lock)
        LOGGER.info("Applied changes on lockfile")

    @staticmethod
    def _update_root_page(client, space, lock, name):
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

        return {"root_page_id": found_root_page.id}, found_root_page

    def _update_vacations(self, client, root_page, lock):
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
            vacations_schema = self._merge_schemas(vacations_old_schema, vacations_schema)
            vacations_collection.set("schema", vacations_schema)
        else:
            vacations_collection = client.get_collection(
                client.create_record("collection", parent=vacations_page, schema=vacations_schema))
            LOGGER.info(f"Created the inbox page collection as {vacations_collection}")

        vacations_collection.name = "Vacations"

        vacations_collection_database_view = space_utils.attach_view_to_collection(
            client, vacations_page, vacations_collection, lock.get("database_view_id"), "table",
            "Database", schema.VACATIONS_DATABASE_VIEW_SCHEMA)
        lock["database_view_id"] = vacations_collection_database_view.id

        vacations_page.set("collection_id", vacations_collection.id)
        vacations_page.set("view_ids", [vacations_collection_database_view.id])

        return lock

    @staticmethod
    def _merge_schemas(old_schema, new_schema):
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        for (schema_item_name, schema_item) in new_schema.items():
            if schema_item["type"] == "select" or schema_item["type"] == "multi_select":
                if schema_item_name in old_schema:
                    old_v = old_schema[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": []
                    }

                    for option in schema_item["options"]:
                        old_option = next((old_o for old_o in old_v["options"] if old_o["value"] == option["value"]),
                                          None)
                        if old_option is not None:
                            combined_schema[schema_item_name]["options"].append({
                                "color": option["color"],
                                "value": option["value"],
                                "id": old_option["id"]
                            })
                        else:
                            combined_schema[schema_item_name]["options"].append(option)
                else:
                    combined_schema[schema_item_name] = schema_item
            else:
                combined_schema[schema_item_name] = schema_item

        return combined_schema
