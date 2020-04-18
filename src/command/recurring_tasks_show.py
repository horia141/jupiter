"""Command for showing the recurring tasks."""

import logging

import command.command as command
import repository.workspaces as workspaces
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
        parser.add_argument("--id", type=str, dest="id", help="The id of the vacations to modify")
        parser.add_argument("--project", dest="project", required=True, help="The project key to add the task to")

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

        # Dump out contents of the recurring tasks

        if ref_id:
            # Print details about a single task
            recurring_task = next(
                v for group in project["recurring_tasks"]["entries"].values()
                for v in group["tasks"] if v["ref_id"] == ref_id)
            print(f'id={recurring_task["ref_id"]} {recurring_task["name"]}' + \
                  f' period={recurring_task["period"]}' + \
                  f' group="{recurring_task["group"]}"' + \
                  f'\n    eisen="{(",".join(recurring_task["eisen"])) if recurring_task["eisen"] else ""}"' + \
                  f' difficulty={recurring_task["difficulty"] or "none"}' + \
                  f' skip_rule={recurring_task["skip_rule"] or "none"}' + \
                  f' suspended={recurring_task["suspended"]}' + \
                  f' must_do={recurring_task["must_do"]}' + \
                  f'\n    due_at_time={recurring_task["due_at_time"] or "none"}' + \
                  f' due_at_day={recurring_task["due_at_day"] or "none"}' + \
                  f' due_at_month={recurring_task["due_at_month"] or "none"}')
        else:
            # Print a summary of all tasks
            for group_name, group in project["recurring_tasks"]["entries"].items():
                print(f'{group_name}:')
                for recurring_task in group["tasks"]:
                    print(f'  id={recurring_task["ref_id"]} {recurring_task["name"]}' + \
                          f' period={recurring_task["period"]}' + \
                          f' group={recurring_task["group"]}')
