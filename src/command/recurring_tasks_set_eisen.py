"""Command for setting the Eisenhower status of a recurring task."""

import logging

from notion.client import NotionClient

import command.command as command
from repository.common import TaskEisen
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.workspaces as workspaces
import space_utils
import schema
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetEisen(command.Command):
    """Command class for setting the Eisenhower status of a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-set-eisen"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the Eisenhower status of a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=[te.value for te in TaskEisen], help="The Eisenhower matrix values to use for task")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        eisen = [TaskEisen(e) for e in args.eisen]

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        # Apply changes locally

        workspace = workspace_repository.load_workspace()

        recurring_task = recurring_tasks_repository.load_recurring_task_by_id(ref_id)
        recurring_task.set_eisen(eisen)
        recurring_tasks_repository.save_recurring_task(recurring_task)

        project = projects_repository.load_project_by_id(recurring_task.project_ref_id)

        # Apply changes in Notion

        # Prepare Notion connection

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
        setattr(recurring_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, [e.value for e in eisen])
        LOGGER.info("Applied Notion changes")

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
            setattr(inbox_task_row, schema.INBOX_TASK_ROW_EISEN_KEY, [e.value for e in eisen])
            LOGGER.info(f"Applied Notion changes to inbox task {inbox_task_row}")
