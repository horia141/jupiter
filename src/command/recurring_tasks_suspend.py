"""Command for suspending of a recurring task."""

import logging

import command.command as command
import service.workspaces as workspaces
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksSuspend(command.Command):
    """Command class for suspending a recurring task."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-suspend"

    @staticmethod
    def description():
        """The description of the command."""
        return "Suspend a recurring task"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="id", required=True, help="The id of the vacations to modify")
        parser.add_argument("--project", type=str, dest="project", help="The key of the project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        project_key = args.project

        # Load local storage

        _ = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        workspace_repository = workspaces.WorkspaceRepository()
        _ = workspace_repository.load_workspace()
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Apply changes locally

        try:
            recurring_task = next(
                v for group in project["recurring_tasks"]["entries"].values()
                for v in group["tasks"] if v["ref_id"] == ref_id)
            recurring_task["suspended"] = True
            storage.save_project(project_key, project)
            LOGGER.info("Modified recurring task")
        except StopIteration:
            LOGGER.error(f"Recurring task with id {ref_id} does not exist")
            return
