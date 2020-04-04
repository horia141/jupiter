"""Command for showing the recurring tasks."""

import logging

import command.command as command
import storage

LOGGER = logging.getLogger(__name__)


class RecurringTasksShow(command.Command):
    """Command class for showing the recurring tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "recurring-tasks-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the list of recurring tasks"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project", required=True, help="The project key to add the task to")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        project_key = args.project

        # Load local storage

        _ = storage.load_lock_file()
        LOGGER.info("Loaded the system lock")
        _ = storage.load_workspace()
        LOGGER.info("Loaded workspace data")
        project = storage.load_project(project_key)
        LOGGER.info("Loaded the project data")

        # Dump out contents of the vacations

        for group_name, group in project["recurring_tasks"]["entries"].items():
            print(f'{group_name}:')
            for recurring_task in group["tasks"]:
                print(f'  id={recurring_task["ref_id"]} {recurring_task["name"]} period={recurring_task["period"]}')
