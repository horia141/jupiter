"""Command for setting the skip rule of a recurring task."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetSkipRule(command.Command):
    """Command class for setting the skip rule of a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-set-skip-rule"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the skip rule of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--skip-rule", dest="skip_rule", help="The skip rule for the task")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        skip_rule = args.skip_rule.strip().lower() if args.skip_rule else None

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        # Apply changes locally

        workspace = workspace_repository.load_workspace()

        recurring_task = recurring_tasks_repository.load_recurring_task_by_id(ref_id)
        recurring_task.skip_rule = skip_rule
        recurring_tasks_repository.save_recurring_task(recurring_task)

        project = projects_repository.load_project_by_id(recurring_task.project_ref_id)

        # Apply changes in Notion

        # First, change the recurring task entry

        client = NotionClient(token_v2=workspace.token)

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["recurring_tasks"]["root_page_id"])
        recurring_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["recurring_tasks"]["database_view_id"],
                collection=recurring_tasks_page.collection) \
            .build_query() \
            .execute()

        recurring_task_row = next(r for r in recurring_tasks_rows if r.ref_id == ref_id)
        recurring_task_row.skip_rule = skip_rule
        LOGGER.info("Applied Notion changes")
