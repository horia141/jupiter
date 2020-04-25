"""Command for removing a recurring task."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.workspaces as workspaces
import space_utils
import storage
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class RecurringTasksArchive(command.Command):
    """Command class for removing a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-archive"

    @staticmethod
    def description():
        """The description of the command."""
        return "Remove a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True, help="The id of the vacations to modify")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        ref_id = basic_validator.entity_id_validate_and_clean(args.ref_id)

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        # Apply changes locally

        workspace = workspace_repository.load_workspace()

        recurring_task = recurring_tasks_repository.load_recurring_task_by_id(ref_id)
        LOGGER.info(f"Removing recurring task {recurring_task.name}")
        recurring_tasks_repository.remove_recurring_task_by_id(ref_id)

        project = projects_repository.load_project_by_id(recurring_task.project_ref_id)

        for inbox_task in inbox_tasks_repository.list_all_inbox_tasks(
                filter_project_ref_id=[project.ref_id],
                filter_recurring_task_ref_id=[recurring_task.ref_id]):
            LOGGER.info(f"Removing recurring task instance {inbox_task.name}")
            inbox_tasks_repository.remove_inbox_task_by_id(inbox_task.ref_id)

        # Apply changes in Notion

        client = NotionClient(token_v2=workspace.token)

        # First, change the recurring task entry

        recurring_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["recurring_tasks"]["root_page_id"])
        recurring_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["recurring_tasks"]["database_view_id"],
                collection=recurring_tasks_page.collection) \
            .build_query() \
            .execute()

        recurring_task_row = next(r for r in recurring_tasks_rows if r.ref_id == ref_id)
        recurring_task_row.archived = True
        LOGGER.info("Removed recurring task from Notion")

        # Then, change every task

        inbox_tasks_page = space_utils.find_page_from_space_by_id(
            client, the_lock["projects"][project.key]["inbox"]["root_page_id"])
        inbox_tasks_rows = client \
            .get_collection_view(
                the_lock["projects"][project.key]["inbox"]["database_view_id"],
                collection=inbox_tasks_page.collection) \
            .build_query() \
            .execute()

        for inbox_task_row in inbox_tasks_rows:
            if inbox_task_row.recurring_task_id != ref_id:
                continue
            inbox_task_row.archived = True
            LOGGER.info(f"Removed inbox task {inbox_task_row}")
