"""Command for associating an inbox task with a big plan."""

import logging

from notion.client import NotionClient

import command.command as command
from repository.common import RefId
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class InboxTasksAssociateBigPlan(command.Command):
    """Command class for associating an inbox task with a big plan."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-associate-big-plan"

    @staticmethod
    def description():
        """The description of the command."""
        return "Associate an inbox task with a big plan"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required="True", help="The if of the big plan")
        parser.add_argument("--big-plan-id", dest="big_plan_ref_id",
                            help="The id of a big plan to associate this task to.")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Parse arguments

        ref_id = args.ref_id
        big_plan_ref_id = RefId(args.big_plan_ref_id) if args.big_plan_ref_id else None

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        workspace = workspace_repository.load_workspace()

        if big_plan_ref_id:
            big_plan = big_plans_repository.load_big_plan_by_id(big_plan_ref_id)

        inbox_task = inbox_tasks_repository.load_inbox_task_by_id(ref_id)

        if inbox_task.recurring_task_ref_id is not None:
            raise Exception(f"Task {inbox_task.name} is an instance of a recurring task and can't be changed")

        inbox_task.big_plan_ref_id = big_plan_ref_id
        inbox_tasks_repository.save_inbox_task(inbox_task)

        project = projects_repository.load_project_by_id(inbox_task.project_ref_id)
        LOGGER.info("Applied local changes")

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=workspace.token)

        # Apply the changes on Notion side

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["inbox"]["root_page_id"])
        inbox_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["inbox"]["database_view_id"],
                collection=inbox_tasks_page.collection) \
            .build_query() \
            .execute()

        inbox_task_row = next(r for r in inbox_tasks_rows if r.ref_id == ref_id)
        if big_plan_ref_id:
            inbox_task_row.big_plan_id = big_plan_ref_id
            inbox_task_row.big_plan = schema.format_name_for_option(big_plan.name)
        else:
            inbox_task_row.big_plan_id = None
            inbox_task_row.big_plan = None
        LOGGER.info("Removed inbox task from Notion")
