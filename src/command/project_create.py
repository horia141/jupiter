"""Command for creating projects."""

import logging

from notion.block import CollectionViewPageBlock
from notion.client import NotionClient

import command.command as command
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class ProjectCreate(command.Command):
    """Command class for creating projects."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create or update a project"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        project_name = args.name

        # Load local storage

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace = storage.load_workspace()
        LOGGER.info("Found workspace file")

        try:
            project = storage.load_project(project_key)
            LOGGER.info("Found project file")
        except IOError:
            project = storage.build_empty_project()
            LOGGER.info("No project file - creating it")

        # Apply the changes Notion side

        client = NotionClient(token_v2=workspace["token"])

        if project_key in system_lock["projects"]:
            project_lock = system_lock["projects"][project_key]
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
            found_root_page = space_utils.find_page_from_page_by_name(system_root_page, project_name)
            LOGGER.info(f"Found the project page via name {found_root_page}")
        if not found_root_page:
            found_root_page = space_utils.create_page_in_page(system_root_page, project_name)
            LOGGER.info(f"Created the root page {found_root_page}")
        found_root_page.title = project_name
        project_lock["root_page_id"] = found_root_page.id

        # Create the inbox.
        project_lock["inbox"] = ProjectCreate._update_inbox(
            client, found_root_page, project_lock.get("inbox", {}))

        # Create the recurring tasks.
        project_lock["recurring_tasks"] = ProjectCreate._update_recurring_tasks(
            client, found_root_page, project_lock.get("recurring_tasks", {}))

        # Create the big plan.
        project_lock["big_plan"] = ProjectCreate._update_big_plan(
            client, found_root_page, project_lock.get("big_plan", {}))

        # Apply the changes locally

        system_lock["projects"][project_key] = project_lock
        storage.save_lock_file(system_lock)
        LOGGER.info("Applied changes to local system lock")

        project["key"] = project_key
        project["name"] = project_name
        storage.save_project(project_key, project)
        workspace["projects"][project_key] = workspace["projects"].get(project_key, {})
        LOGGER.info("Applied changes to local project file")
        storage.save_workspace(workspace)
        LOGGER.info("Applied changes to workspace")

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
            inbox_schema = ProjectCreate._merge_schemas(inbox_old_schema, inbox_schema)
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
    def _update_recurring_tasks(client, root_page, recurring_task_lock):

        if "root_page_id" in recurring_task_lock:
            found_recurring_tasks_page = space_utils.find_page_from_space_by_id(
                client, recurring_task_lock["root_page_id"])
            LOGGER.info(f"Found the recurring tasks page via id {found_recurring_tasks_page}")
        else:
            found_recurring_tasks_page = space_utils.find_page_from_page_by_name(root_page, "Recurring Tasks")
            LOGGER.info(f"Found the recurring tasks page via name {found_recurring_tasks_page}")
        if not found_recurring_tasks_page:
            found_recurring_tasks_page = root_page.children.add_new(CollectionViewPageBlock)
            LOGGER.info(f"Created the recurring tasks page {found_recurring_tasks_page}")
        recurring_task_lock["root_page_id"] = found_recurring_tasks_page.id

        recurring_tasks_schema = schema.get_recurring_tasks_schema()
        recurring_tasks_page = found_recurring_tasks_page

        recurring_tasks_collection_id = recurring_tasks_page.get("collection_id")
        if recurring_tasks_collection_id:
            recurring_tasks_collection = client.get_collection(recurring_tasks_collection_id)
            LOGGER.info(
                f"Found the already existing recurring tasks page collection via id {recurring_tasks_collection}")
            recurring_tasks_old_schema = recurring_tasks_collection.get("schema")
            recurring_tasks_schema = ProjectCreate._merge_schemas(recurring_tasks_old_schema, recurring_tasks_schema)
            recurring_tasks_collection.set("schema", recurring_tasks_schema)
            LOGGER.info(f"Updated the recurring tasks page collection schema")
        else:
            recurring_tasks_collection = client.get_collection(
                client.create_record("collection", parent=recurring_tasks_page, schema=recurring_tasks_schema))
            LOGGER.info(f"Created the recurring tasks collection {recurring_tasks_collection}")
        recurring_tasks_collection.name = "Recurring Tasks"

        recurring_tasks_collection_kanban_all_view = space_utils.attach_view_to_collection(
            client, recurring_tasks_page, recurring_tasks_collection,
            recurring_task_lock.get("kanban_all_view_id"), "board",
            "Kanban All", schema.RECURRING_TASKS_KANBAN_ALL_SCHEMA)
        recurring_task_lock["kanban_all_view_id"] = recurring_tasks_collection_kanban_all_view.id

        recurring_tasks_collection_database_view = space_utils.attach_view_to_collection(
            client, recurring_tasks_page, recurring_tasks_collection,
            recurring_task_lock.get("database_view_id"), "table",
            "Database", schema.RECURRING_TASKS_DATABASE_VIEW_SCHEMA)
        recurring_task_lock["database_view_id"] = recurring_tasks_collection_database_view.id

        recurring_tasks_page.set("collection_id", recurring_tasks_collection.id)
        recurring_tasks_page.set("view_ids", [
            recurring_tasks_collection_kanban_all_view.id,
            recurring_tasks_collection_database_view.id
        ])

        return recurring_task_lock

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
            big_plan_schema = ProjectCreate._merge_schemas(big_plan_old_schema, big_plan_schema)
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

        big_plan_collection_database_view = space_utils.attach_view_to_collection(
            client, big_plan_page, big_plan_collection, big_plan_lock.get("database_view_id"), "table",
            "Database", schema.BIG_PLAN_DATABASE_VIEW_SCHEMA)
        big_plan_lock["database_view_id"] = big_plan_collection_database_view.id

        big_plan_page.set("collection_id", big_plan_collection.id)
        big_plan_page.set("view_ids", [
            big_plan_collection_kanban_all_view.id,
            big_plan_collection_database_view.id
        ])

        return big_plan_lock

    @staticmethod
    def _merge_schemas(old_schema, new_schema):

        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        # As another special case, the recurring tasks group key is left to whatever value it had
        # before since this thing is managed by the other flows!
        for (schema_item_name, schema_item) in new_schema.items():
            if schema_item_name in (schema.INBOX_BIGPLAN_KEY, schema.RECURRING_TASKS_GROUP_KEY):
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
