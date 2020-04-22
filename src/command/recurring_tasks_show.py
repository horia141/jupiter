"""Command for showing the recurring tasks."""

import logging

import command.command as command
import repository.projects as projects
import repository.recurring_tasks as recurring_tasks

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
        parser.add_argument("--project", type=str, dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        ref_id = args.id
        project_keys = args.project_keys if len(args.project_keys) > 0 else None

        # Load local storage

        projects_repository = projects.ProjectsRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()

        # Dump out contents of the recurring tasks

        if ref_id:
            # Print details about a single task
            recurring_task = recurring_tasks_repository.load_recurring_task_by_id(ref_id)
            print(f'id={recurring_task.ref_id} {recurring_task.name}' +
                  f' period={recurring_task.period.value}' +
                  f' group="{recurring_task.group}"' +
                  f'\n    eisen="{(",".join(e.value for e in recurring_task.eisen)) if recurring_task.eisen else ""}"' +
                  f' difficulty={recurring_task.difficulty.value if recurring_task.difficulty else "none"}' +
                  f' skip_rule={recurring_task.skip_rule or "none"}' +
                  f' suspended={recurring_task.suspended}' +
                  f' must_do={recurring_task.must_do}' +
                  f'\n    due_at_time={recurring_task.due_at_time or "none"}' +
                  f' due_at_day={recurring_task.due_at_day or "none"}' +
                  f' due_at_month={recurring_task.due_at_month or "none"}')
        else:
            all_projects = projects_repository.list_all_projects(filter_keys=project_keys)
            # Print a summary of all tasks
            for recurring_task in \
                    recurring_tasks_repository\
                            .list_all_recurring_tasks(filter_project_ref_id=(p.ref_id for p in all_projects)):
                print(f'  id={recurring_task.ref_id} {recurring_task.name}' +
                      f' period={recurring_task.period.value}' +
                      f' group={recurring_task.group}')
