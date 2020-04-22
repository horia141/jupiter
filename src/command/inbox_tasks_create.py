"""Command for creating an inbox task."""

import logging

from notion.client import NotionClient
import pendulum

import command.command as command
from repository.common import TaskEisen, TaskDifficulty
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class InboxTasksCreate(command.Command):
    """Command class for creating inbox tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-create"

    @staticmethod
    def description():
        """The description of the command."""
        return "Create an inbox task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project", required="True",
                            help="The key of the project")
        parser.add_argument("--name", dest="name", required=True, help="The name of the inbox task")
        parser.add_argument("--big-plan-id", dest="big_plan_ref_id",
                            help="The id of a big plan to associate this task to.")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=[te.value for te in TaskEisen], help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", choices=[td.value for td in TaskDifficulty],
                            help="The difficulty to use for tasks")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project
        name = args.name.strip()
        big_plan_ref_id = args.big_plan_ref_id
        eisen = [TaskEisen(e.strip().lower()) for e in args.eisen]
        difficulty = TaskDifficulty(args.difficulty) if args.difficulty else None
        due_date = pendulum.parse(args.due_date) if args.due_date else None

        if len(name) == 0:
            raise Exception("Must provide a non-empty name")

        right_now = pendulum.now()

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        big_plans_repository = big_plans.BigPlansRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)

        if big_plan_ref_id:
            big_plan = big_plans_repository.load_big_plan_by_id(big_plan_ref_id)

        # Apply changes locally.

        new_inbox_task = inbox_tasks_repository.create_inbox_task(
            project_ref_id=project.ref_id,
            big_plan_ref_id=big_plan_ref_id,
            recurring_task_ref_id=None,
            created_date=right_now,
            name=name,
            archived=False,
            status=inbox_tasks.InboxTaskStatus.ACCEPTED,
            eisen=eisen,
            difficulty=difficulty,
            due_date=due_date,
            recurring_task_timeline=None)

        # Apply the changes Notion side.

        client = NotionClient(token_v2=workspace.token)

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project_key]["inbox"]["root_page_id"])
        inbox_tasks_collection = inbox_tasks_page.collection

        new_inbox_task_row = inbox_tasks_collection.add_row()
        new_inbox_task_row.ref_id = new_inbox_task.ref_id
        if big_plan_ref_id:
            new_inbox_task_row.big_plan_id = big_plan_ref_id
            new_inbox_task_row.big_plan = schema.format_name_for_option(big_plan.name)
        new_inbox_task_row.recurring_task_id = None
        new_inbox_task_row.created_date = new_inbox_task.created_date
        new_inbox_task_row.title = new_inbox_task.name
        new_inbox_task_row.archived = False
        new_inbox_task_row.status = new_inbox_task.status.value
        setattr(new_inbox_task_row, "eisenhower", [e.value for e in new_inbox_task.eisen])
        setattr(
            new_inbox_task_row, "difficulty", new_inbox_task.difficulty.value if new_inbox_task.difficulty else None)
        new_inbox_task_row.due_date = new_inbox_task.due_date
        setattr(new_inbox_task_row, "from_script", True)
        setattr(new_inbox_task_row, "recurring_period", None)
        setattr(new_inbox_task_row, "recurring_timeline", None)
        LOGGER.info("Applied Notion changes")
