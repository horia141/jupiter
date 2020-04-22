"""Command for adding a recurring task."""

import logging
import re
import uuid

from notion.client import NotionClient

import command.command as command
from repository.common import TaskPeriod, TaskEisen, TaskDifficulty
import repository.recurring_tasks as recurring_tasks
import repository.projects as projects
import repository.workspaces as workspaces
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
        parser.add_argument("--period", dest="period", choices=[tp.value for tp in TaskPeriod], required=True,
                            help="The period for the recurring task")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=[te.value for te in TaskEisen], help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", choices=[td.value for td in TaskDifficulty],
                            help="The difficulty to use for tasks")
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
        group = args.group.strip()
        period = TaskPeriod(args.period)
        eisen = [e.strip().lower() for e in args.eisen]
        difficulty = TaskDifficulty(args.difficulty) if args.difficulty else None
        due_at_time = args.due_at_time.strip().lower() if args.due_at_time else None
        due_at_day = args.due_at_day
        due_at_month = args.due_at_month
        must_do = args.must_do if args.must_do else False
        skip_rule = args.skip_rule.strip().lower() if args.skip_rule else None
        project_key = args.project

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        if len(group) == 0:
            raise Exception("Most provide a non-empty group")

        if any(e not in [te.value for te in TaskEisen] for e in eisen):
            raise Exception(f"Invalid eisenhower values {eisen}")

        if due_at_time:
            if not re.match("^[0-9][0-9]:[0-9][0-9]$", due_at_time):
                raise Exception(f"Invalid due time value '{due_at_time}'")

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)

        # Apply changes locally

        new_recurring_task = recurring_tasks_repository.create_recurring_task(
            project_ref_id=project.ref_id, archived=False, name=name, period=period,
            group=recurring_tasks.RecurringTaskGroup(group), eisen=[TaskEisen(e) for e in eisen], difficulty=difficulty,
            due_at_time=due_at_time, due_at_day=due_at_day, due_at_month=due_at_month, suspended=False,
            skip_rule=skip_rule, must_do=must_do)

        # Apply changes in Notion

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["recurring_tasks"]["root_page_id"])

        # First, update the recurring tasks collection schema, with the full group
        # structure.
        recurring_tasks_collection = recurring_tasks_page.collection
        recurring_tasks_schema = recurring_tasks_collection.get("schema")
        all_local_groups = {k.group.lower().strip(): k.group
                            for k in recurring_tasks_repository.list_all_recurring_tasks()}
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
        new_recurring_task_row.ref_id = new_recurring_task.ref_id
        new_recurring_task_row.archived = False
        new_recurring_task_row.title = name
        new_recurring_task_row.group = group
        new_recurring_task_row.period = period.value
        setattr(new_recurring_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, [e.value for e in eisen])
        new_recurring_task_row.difficulty = difficulty.value if difficulty else None
        new_recurring_task_row.due_at_time = due_at_time
        new_recurring_task_row.due_at_day = due_at_day
        new_recurring_task_row.due_at_month = due_at_month
        new_recurring_task_row.must_do = must_do
        new_recurring_task_row.skip_rule = skip_rule
        LOGGER.info("Applied Notion changes")
