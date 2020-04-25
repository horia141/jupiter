"""Command for removing archived tasks from a project."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import storage
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class RemoveArchivedTasks(command.Command):
    """Command class for removing archived tasks from a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "remove-archived-tasks"

    @staticmethod
    def description():
        """The description of the command."""
        return "Archive tasks which are done"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")
        parser.add_argument("--period", default=[], action="append",
                            help="The period for which the remove should happen. Defaults to all")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        project_key = basic_validator.project_key_validate_and_clean(args.project_key)
        period_filter = frozenset(basic_validator.recurring_task_period_validate_and_clean(p) for p in args.period) \
            if len(args.period) > 0 else None
        dry_run = args.dry_run

        # Load local storage.

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_reposittory = projects.ProjectsRepository()

        workspace = workspace_repository.load_workspace()
        _ = projects_reposittory.load_project_by_key(project_key)

        LOGGER.info("Found project file")

        client = NotionClient(token_v2=workspace.token)

        project_lock = system_lock["projects"][project_key]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        archived_tasks = page.build_query().execute()

        for archived_task in archived_tasks:
            task_period = getattr(archived_task, schema.INBOX_TASK_ROW_PERIOD_KEY)
            if not task_period:
                task_period = ""
            if archived_task.status != schema.ARCHIVED_STATUS:
                continue
            if period_filter and (task_period.lower() not in period_filter):
                LOGGER.info(f"Skipping '{archived_task.name}' on account of period filtering")
                continue
            LOGGER.info(f"Removing '{archived_task.name}'")
            if not dry_run:
                archived_task.remove()
