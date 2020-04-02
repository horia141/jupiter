"""Command for adding a recurring task."""

import logging
import uuid

from notion.client import NotionClient

import command.command as command
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksCreate(command.Command):
    """Command class for creating a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create a new recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", dest="name", required=True, help="The name of the recurring task")
        parser.add_argument("--group", dest="group", required=True, help="The group for the recurring task")
        parser.add_argument("--period", dest="period", required=True, help="The period for the recurring task")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", help="The difficulty to use for tasks")
        parser.add_argument("--due-at-time", dest="due_at_time", metavar="HH:MM", help="The time a task will be due on")
        parser.add_argument("--due-at-day", type=int, dest="due_at_day", metavar="DAY",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--due-at-month", type=int, dest="due_at_month", metavar="MONTH",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--must-do", dest="must_do", default=False, action="store_true",
                            help="Whether to treat this task as must do or not")
        parser.add_argument("--skip-rule", dest="skip_rule", help="The skip rule for the task")
        parser.add_argument("--project", dest="project", required=True, help="The project key to add the task to")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        name = args.name.strip()
        group = args.group
        period = args.period
        eisen = args.eisen
        difficulty = args.difficulty
        due_at_time = args.due_at_time
        due_at_day = args.due_at_day
        due_at_month = args.due_at_month
        must_do = args.must_do
        skip_rule = args.skip_rule
        project_key = args.project

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded system lock")
        workspace = storage.load_workspace()
        LOGGER.info("Loaded workspace data")
        project = storage.load_project(project_key)
        LOGGER.info("Loaded project data")

        # Prepare Notion connection

        # Apply changes locally

        new_recurring_task = {
            "ref_id": str(project["recurring_tasks"]["next_idx"]),
            "name": name,
            "period": period,
            "group": group,
            "eisen": eisen,
            "difficulty": difficulty,
            "due_at_time": due_at_time,
            "due_at_day": due_at_day,
            "due_at_month": due_at_month,
            "suspended": False,
            "skip_rule": skip_rule,
            "must_do": must_do
        }
        project["recurring_tasks"]["next_idx"] = project["recurring_tasks"]["next_idx"] + 1
        if group in project["recurring_tasks"]["entries"]:
            project["recurring_tasks"]["entries"][group]["tasks"].append(new_recurring_task)
        else:
            project["recurring_tasks"]["entries"][group] = {
                "format": "{name}",
                "tasks": [new_recurring_task]
            }
        storage.save_project(project_key, project)
        LOGGER.info("Applied local changes")

        # Apply changes in Notion

        client = NotionClient(token_v2=workspace["token"])

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["recurring_tasks"]["root_page_id"])

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

        # Now, add the new task

        new_recurring_task_row = recurring_tasks_collection.add_row()
        new_recurring_task_row.ref_id = new_recurring_task["ref_id"]
        new_recurring_task_row.title = name
        new_recurring_task_row.group = group
        new_recurring_task_row.period = period
        setattr(new_recurring_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, eisen)
        new_recurring_task_row.difficulty = difficulty
        new_recurring_task_row.due_at_time = due_at_time
        new_recurring_task_row.due_at_day = due_at_day
        new_recurring_task_row.due_at_month = due_at_month
        new_recurring_task_row.must_do = must_do
        new_recurring_task_row.skip_rule = skip_rule
        LOGGER.info("Applied Notion changes")
