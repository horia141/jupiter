"""Command for archiving done tasks."""

import logging
from typing import Dict

from notion.client import NotionClient

import command.command as command
from models.basic import EntityId, BasicValidator
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.workspaces as workspaces
import schema
import storage

DONE_STATUS = [schema.DONE_STATUS, schema.NOT_DONE_STATUS]
LOGGER = logging.getLogger(__name__)


class InboxTasksArchiveDone(command.Command):
    """Command class for archiving done tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-archive-done"

    @staticmethod
    def description():
        """The description of the command."""
        return "Archive tasks which are done"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments

        project_key = basic_validator.project_key_validate_and_clean(args.project_key)

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()

        workspace = workspace_repository.load_workspace()
        project = projects_repository.load_project_by_key(project_key)
        all_inbox_tasks = inbox_tasks_repository.list_all_inbox_tasks(filter_project_ref_id=[project.ref_id])
        all_inbox_tasks_set: Dict[EntityId, inbox_tasks.InboxTask] = {it.ref_id: it for it in all_inbox_tasks}

        # Apply changes locally

        for inbox_task in all_inbox_tasks:
            if not inbox_task.is_considered_done:
                continue

            LOGGER.info(f"Archived task {inbox_task.name} with status={inbox_task.status}")
            inbox_task.archived = True
            inbox_tasks_repository.save_inbox_task(inbox_task)

        client = NotionClient(token_v2=workspace.token)

        project_lock = system_lock["projects"][project_key]
        root_page = client.get_block(project_lock["inbox"]["root_page_id"])
        page = client.get_collection_view(project_lock["inbox"]["database_view_id"], collection=root_page.collection)

        all_inbox_tasks_row = page.build_query().execute()

        for inbox_task_row in all_inbox_tasks_row:
            if inbox_task_row.ref_id not in all_inbox_tasks_set:
                LOGGER.warning(f"Skipping Notion-only task {inbox_task_row.title}. You may need to re-sync")
                continue

            inbox_task = all_inbox_tasks_set[inbox_task_row.ref_id]
            inbox_task_row.archived = inbox_task.archived
            if inbox_task.archived:
                LOGGER.info(f"Archiving '{inbox_task_row.title}'")
