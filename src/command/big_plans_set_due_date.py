"""Command for setting the due date of a big plan."""

import logging

from notion.client import NotionClient
import pendulum

import command.command as command
import repository.big_plans as big_plans
import repository.projects as projects
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class BigPlansSetDueDate(command.Command):
    """Command class for setting the due date of a big plan."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-set-due-date"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the due date of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--due-date", dest="due_date", help="The due date of the big plan")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        due_date = pendulum.parse(args.due_date) if args.due_date else None

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        # Apply changes locally

        workspace = workspace_repository.load_workspace()

        big_plan = big_plans_repository.load_big_plan_by_id(ref_id)
        big_plan.due_date = due_date
        big_plans_repository.save_big_plan(big_plan)

        project = projects_repository.load_project_by_id(big_plan.project_ref_id)

        # Apply changes in Notion

        # Prepare Notion connection

        client = NotionClient(token_v2=workspace.token)

        # First, change the recurring task entry

        big_plans_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["big_plan"]["root_page_id"])
        big_plans_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["big_plan"]["database_view_id"],
                collection=big_plans_page.collection) \
            .build_query() \
            .execute()

        big_plan_row = next(r for r in big_plans_rows if r.ref_id == ref_id)
        big_plan_row.due_date = big_plan.due_date
        LOGGER.info("Applied Notion changes")
