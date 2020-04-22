"""Command for setting the status of an inbox task."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class InboxTasksSetStatus(command.Command):
    """Command class for setting the status of an inbox task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-set-status"

    @staticmethod
    def description():
        """The description of the command."""
        return "Set the status an inbox task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", dest="ref_id", required="True", help="The if of the big plan")
        parser.add_argument("--status", dest="status", required=True,
                            choices=[bps.value for bps in inbox_tasks.InboxTaskStatus],
                            help="The status of the inbox task")
    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Parse arguments

        ref_id = args.ref_id
        status = inbox_tasks.InboxTaskStatus(args.status.strip().lower())

        # Load local storage

        the_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        projects_repository = projects.ProjectsRepository()

        workspace = workspace_repository.load_workspace()

        inbox_task = inbox_tasks_repository.load_inbox_task_by_id(ref_id)
        inbox_task.set_status(status)
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
        inbox_task_row.status = status.value
        LOGGER.info("Removed inbox task from Notion")
