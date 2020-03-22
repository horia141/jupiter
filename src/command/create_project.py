"""Command for creating projects."""

import logging

from notion.block import CollectionViewPageBlock
from notion.client import NotionClient
import yaml

import command.command as command
import lockfile
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class CreateProject(command.Command):
    """Command class for creating projects."""

    @staticmethod
    def name():
        """The name of the command."""
        return "create-project"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create or update a project"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("tasks", help="The tasks file")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        workspace = storage.load_workspace()

        with open(args.tasks, "r") as tasks_file:
            tasks = yaml.safe_load(tasks_file)

        client = NotionClient(token_v2=workspace["token"])

        self._update_project(client, tasks)

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
            if schema_item_name == schema.INBOX_BIGPLAN_KEY:
                combined_schema[schema_item_name] = old_schema[schema_item_name] \
                    if (schema_item_name in old_schema and old_schema[schema_item_name]["type"] == "select") \
                    else schema_item
            elif schema_item["type"] == "select" or schema_item["type"] == "multi_select":
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

    @staticmethod
    def _update_inbox(client, root_page, inbox_lock):

        if "root_page_id" in inbox_lock:
            inbox_page = space_utils.find_page_from_space_by_id(client, inbox_lock["root_page_id"])
            LOGGER.info(f"Found the inbox page via id {inbox_page}")
        else:
            inbox_page = space_utils.find_page_from_page_by_name(root_page, "Inbox")
            LOGGER.info(f"Found the inbox page via name {inbox_page}")
        if not inbox_page:
            inbox_page = root_page.children.add_new(CollectionViewPageBlock)
            LOGGER.info(f"Created the inbox page {inbox_page}")
        inbox_lock["root_page_id"] = inbox_page.id

        inbox_schema = schema.get_inbox_schema()

        inbox_collection_id = inbox_page.get("collection_id")
        if inbox_collection_id:
            inbox_collection = client.get_collection(inbox_collection_id)
            LOGGER.info(f"Found the already existing inbox page collection via id {inbox_collection}")
            inbox_old_schema = inbox_collection.get("schema")
            inbox_schema = CreateProject._merge_schemas(inbox_old_schema, inbox_schema)
            inbox_collection.set("schema", inbox_schema)
            LOGGER.info(f"Updated the inbox page collection schema")
        else:
            inbox_collection = client.get_collection(
                client.create_record("collection", parent=inbox_page, schema=inbox_schema))
            LOGGER.info(f"Created the inbox page collection as {inbox_collection}")
        inbox_collection.name = "Inbox"

        inbox_collection_kanban_all_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("kanban_all_view_id"), "board", "Kanban All",
            schema.INBOX_KANBAN_ALL_VIEW_SCHEMA)
        inbox_lock["kanban_all_view_id"] = inbox_collection_kanban_all_view.id

        inbox_collection_kanban_urgent_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("kanban_urgent_view_id"), "board",
            "Kanban Urgent", schema.INBOX_KANBAN_URGENT_VIEW_SCHEMA)
        inbox_lock["kanban_urgent_view_id"] = inbox_collection_kanban_urgent_view.id

        inbox_collection_kanban_due_today_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("kanban_due_today_view_id"), "board",
            "Kanban Due Today", schema.INBOX_KANBAN_DUE_TODAY_VIEW_SCHEMA)
        inbox_lock["kanban_due_today_view_id"] = inbox_collection_kanban_due_today_view.id

        inbox_collection_kanban_due_this_week_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("kanban_due_this_week_view_id"), "board",
            "Kanban Due This Week", schema.INBOX_KANBAN_DUE_THIS_WEEK_VIEW_SCHEMA)
        inbox_lock["kanban_due_this_week_view_id"] = inbox_collection_kanban_due_this_week_view.id

        inbox_collection_kanban_due_this_month_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("kanban_due_this_month_view_id"), "board",
            "Kanban Due This Month", schema.INBOX_KANBAN_DUE_THIS_MONTH_VIEW_SCHEMA)
        inbox_lock["kanban_due_this_month_view_id"] = inbox_collection_kanban_due_this_month_view.id

        inbox_collection_calendar_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("calendar_view_id"), "calendar",
            "Not Completed By Date", schema.INBOX_CALENDAR_VIEW_SCHEMA)
        inbox_lock["calendar_view_id"] = inbox_collection_calendar_view.id

        inbox_collection_database_view = space_utils.attach_view_to_collection(
            client, inbox_page, inbox_collection, inbox_lock.get("database_view_id"), "table",
            "Database", schema.INBOX_DATABASE_VIEW_SCHEMA)
        inbox_lock["database_view_id"] = inbox_collection_database_view.id

        inbox_page.set("collection_id", inbox_collection.id)
        inbox_page.set("view_ids", [
            inbox_collection_kanban_all_view.id,
            inbox_collection_kanban_urgent_view.id,
            inbox_collection_kanban_due_today_view.id,
            inbox_collection_kanban_due_this_week_view.id,
            inbox_collection_kanban_due_this_month_view.id,
            inbox_collection_calendar_view.id,
            inbox_collection_database_view.id
        ])

        return inbox_lock

    @staticmethod
    def _update_big_plan(client, root_page, big_plan_lock):

        if "root_page_id" in big_plan_lock:
            found_big_plan_page = space_utils.find_page_from_space_by_id(client, big_plan_lock["root_page_id"])
            LOGGER.info(f"Found the big plan page via id {found_big_plan_page}")
        else:
            found_big_plan_page = space_utils.find_page_from_page_by_name(root_page, "Big Plan")
            LOGGER.info(f"Found the big plan page via name {found_big_plan_page}")
        if not found_big_plan_page:
            found_big_plan_page = root_page.children.add_new(CollectionViewPageBlock)
            LOGGER.info(f"Created the big plan page {found_big_plan_page}")
        big_plan_lock["root_page_id"] = found_big_plan_page.id

        big_plan_schema = schema.get_big_plan_schema()

        big_plan_page = found_big_plan_page

        big_plan_collection_id = big_plan_page.get("collection_id")
        if big_plan_collection_id:
            big_plan_collection = client.get_collection(big_plan_collection_id)
            LOGGER.info(f"Found the already existing big plan page collection via id {big_plan_collection}")
            big_plan_old_schema = big_plan_collection.get("schema")
            big_plan_schema = CreateProject._merge_schemas(big_plan_old_schema, big_plan_schema)
            big_plan_collection.set("schema", big_plan_schema)
            LOGGER.info(f"Updated the big plan page collection schema")
        else:
            big_plan_collection = client.get_collection(
                client.create_record("collection", parent=big_plan_page, schema=big_plan_schema))
            LOGGER.info(f"Created the big plan collection {big_plan_collection}")
        big_plan_collection.name = "Big Plan"

        big_plan_collection_kanban_all_view = space_utils.attach_view_to_collection(
            client, big_plan_page, big_plan_collection, big_plan_lock.get("kanban_all_view_id"), "board",
            "Kanban All", schema.BIG_PLAN_KANBAN_ALL_SCHEMA)
        big_plan_lock["kanban_all_view_id"] = big_plan_collection_kanban_all_view.id

        big_plan_page.set("collection_id", big_plan_collection.id)
        big_plan_page.set("view_ids", [big_plan_collection_kanban_all_view.id])

        return big_plan_lock

    @staticmethod
    def _update_project(client, project_desc):

        name = project_desc["name"]
        key = project_desc["key"]

        system_lock = lockfile.load_lock_file()

        if key in system_lock["projects"]:
            project_lock = system_lock["projects"][key]
            LOGGER.info("Project already in system lock")
        else:
            project_lock = {}
            LOGGER.info("Project not in system lock")

        system_root_page = space_utils.find_page_from_space_by_id(client, system_lock["root_page"]["root_page_id"])
        LOGGER.info(f"Found the root page via id {system_root_page}")

        # Create the root page.
        if "root_page_id" in project_lock:
            found_root_page = space_utils.find_page_from_space_by_id(client, project_lock["root_page_id"])
            LOGGER.info(f"Found the project page via id {found_root_page}")
        else:
            LOGGER.info("Attempting to find project page via name in full space")
            found_root_page = space_utils.find_page_from_page_by_name(system_root_page, name)
            LOGGER.info(f"Found the project page via name {found_root_page}")
        if not found_root_page:
            found_root_page = space_utils.create_page_in_page(system_root_page, name)
            LOGGER.info(f"Created the root page {found_root_page}")
        project_lock["root_page_id"] = found_root_page.id

        # Create the inbox.
        project_lock["inbox"] = CreateProject._update_inbox(client, found_root_page, project_lock.get("inbox", {}))

        # Create the big plan.
        project_lock["big_plan"] = CreateProject._update_big_plan(
            client, found_root_page, project_lock.get("big_plan", {}))

        system_lock["projects"][key] = project_lock
        lockfile.save_lock_file(system_lock)
