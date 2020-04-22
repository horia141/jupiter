"""Command for removing a project."""

import logging

from notion.client import NotionClient

import command.command as command
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks
import repository.workspaces as workspaces
import space_utils
import storage

LOGGER = logging.getLogger(__name__)


class ProjectArchive(command.Command):
    """Command class for remove a project."""

    @staticmethod
    def name():
        """The name of the command."""
        return "project-archive"

    @staticmethod
    def description():
        """The description of the command."""
        return "Remove a project"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        # Parse arguments

        project_key = args.project

        # Load local storage

        system_lock = storage.load_lock_file()
        LOGGER.info("Found system lock")

        workspace_repository = workspaces.WorkspaceRepository()
        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        workspace = workspace_repository.load_workspace()

        LOGGER.info("Removing project")
        project = projects_repository.load_project_by_key(project_key)
        projects_repository.remove_project_by_key(project_key)

        for inbox_task in inbox_tasks_repository.list_all_inbox_tasks(filter_project_ref_id=[project.ref_id]):
            LOGGER.info(f"Removing inbox task {inbox_task.name}")
            inbox_tasks_repository.remove_inbox_task_by_id(inbox_task.ref_id)

        for recurring_task in recurring_tasks_repository.\
                list_all_recurring_tasks(filter_project_ref_id=[project.ref_id]):
            LOGGER.info(f"Removing recurring task {recurring_task.name}")
            recurring_tasks_repository.remove_recurring_task_by_id(recurring_task.ref_id)

        for big_plan in big_plans_repository.list_all_big_plans(filter_project_ref_id=[project.ref_id]):
            LOGGER.info(f"Removing big plan {big_plan.name}")
            big_plans_repository.remove_big_plan_by_id(big_plan.ref_id)

        # Retrieve or create the Notion page for the workspace

        client = NotionClient(token_v2=workspace.token)

        # Apply the changes on Notion side

        if project_key in system_lock["projects"]:
            project_lock = system_lock["projects"][project_key]
            LOGGER.info("Project already in system lock")
        else:
            project_lock = {}
            LOGGER.info("Project not in system lock")

        project_root_page = space_utils.find_page_from_space_by_id(client, project_lock["root_page_id"])
        LOGGER.info(f"Found the root page via id {project_root_page}")

        project_root_page.remove()
        LOGGER.info("Removed Notion structures")

        # Apply the changes to the local side
        del system_lock["projects"][project_key]
        storage.save_lock_file(system_lock)
        LOGGER.info("Removed from lockfile")

        workspace_repository.save_workspace(workspace)
        LOGGER.info("Removed project from workspace")
