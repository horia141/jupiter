"""Command for setting the group of a recurring task."""

import logging
import uuid

from notion.client import NotionClient

import command.command as command
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetGroup(command.Command):
    """Command class for setting the group of a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-set-group"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the group of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--group", dest="group", required=True, help="The group of the recurring task")
        parser.add_argument("--project", type=str, dest="project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        group = args.group.strip()
        project_key = args.project

        if len(group) == 0:
            raise Exception("Most provide a non-empty group")

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace["token"])

        # Apply changes locally

        try:
            recurring_task = next(
                v for group in project["recurring_tasks"]["entries"].values()
                for v in group["tasks"] if v["ref_id"] == ref_id)

            if group == recurring_task["group"]:
                LOGGER.info("Same group as before")
                return

            old_group = recurring_task["group"]
            recurring_task["group"] = group

            if group in project["recurring_tasks"]["entries"]:
                project["recurring_tasks"]["entries"][group]["tasks"].append(recurring_task)
            else:
                project["recurring_tasks"]["entries"][group] = {
                    "format": "{name}",
                    "tasks": [recurring_task]
                }

            idx = 0
            for recurring_task_match in project["recurring_tasks"]["entries"][old_group]["tasks"]:
                if recurring_task_match["ref_id"] != ref_id:
                    idx += 1
                    continue
                del project["recurring_tasks"]["entries"][old_group]["tasks"][idx]
                break

            storage.save_project(project_key, project)
            LOGGER.info("Modified recurring task")
        except StopIteration:
            LOGGER.error(f"Recurring task with id {ref_id} does not exist")
            return

        # Apply changes in Notion

        # First, change the recurring task entry

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["recurring_tasks"]["root_page_id"])
        recurring_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project_key]["recurring_tasks"]["database_view_id"],
                collection=recurring_tasks_page.collection) \
            .build_query() \
            .execute()

        # First, update the recurring tasks collection schema, with the full group
        # structure.
        recurring_tasks_collection = recurring_tasks_page.collection
        recurring_tasks_schema = recurring_tasks_collection.get("schema")
        all_local_groups = {k.lower().strip(): k for k in project["recurring_tasks"]["entries"].keys()}
        all_notion_groups = recurring_tasks_schema[schema.RECURRING_TASKS_GROUP_KEY]
        if "options" not in all_notion_groups:
            all_notion_groups["options"] = []
        all_notion_groups_key = [k["value"].lower().strip() for k in all_notion_groups["options"]]
        for (local_group_key, local_group_value) in all_local_groups.items():
            if local_group_key in all_notion_groups_key:
                continue
            all_notion_groups["options"].append({
                "color": schema.get_stable_color(local_group_key),
                "id": str(uuid.uuid4()),
                "value": schema.format_name_for_option(local_group_value)
            })
        recurring_tasks_collection.set("schema", recurring_tasks_schema)

        recurring_task_row = next(r for r in recurring_tasks_rows if r.ref_id == ref_id)
        recurring_task_row.group = group
        LOGGER.info("Applied Notion changes")
