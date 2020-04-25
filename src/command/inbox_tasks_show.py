"""Command for showing the inbox tasks."""

import logging

import command.command as command
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.recurring_tasks as recurring_tasks
import repository.projects as projects
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class InboxTasksShow(command.Command):
    """Command class for showing the inbox tasks."""

    @staticmethod
    def name():
        """The name of the command."""
        return "inbox-tasks-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the list of inbox tasks"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", help="The id of the vacations to modify")
        parser.add_argument("--project", dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        ref_id = basic_validator.entity_id_validate_and_clean(args.ref_id) if args.ref_id else None
        project_keys = [basic_validator.project_key_validate_and_clean(p) for p in args.project_keys]\
            if len(args.project_keys) > 0 else None

        # Load local storage

        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        recurring_tasks_repository = recurring_tasks.RecurringTasksRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        # Dump out contents of the recurring tasks

        if ref_id:
            # Print details about a single task
            inbox_task = inbox_tasks_repository.load_inbox_task_by_id(ref_id)
            big_plan = None
            recurring_task = None
            if inbox_task.big_plan_ref_id:
                big_plan = big_plans_repository.load_big_plan_by_id(inbox_task.big_plan_ref_id)
            elif inbox_task.recurring_task_ref_id:
                recurring_task = recurring_tasks_repository.load_recurring_task_by_id(inbox_task.recurring_task_ref_id)
            print(f'id={inbox_task.ref_id} {inbox_task.name}' +
                  f' status={inbox_task.status.value}' +
                  f' archived="{inbox_task.archived}"' +
                  (f' big_plan="{big_plan.name}"' if big_plan else "") +
                  (f' recurring_task="{recurring_task.name}"' if recurring_task else "") +
                  f' due_date="{inbox_task.due_date.to_datetime_string() if inbox_task.due_date else ""}"' +
                  f'\n    created_date="{inbox_task.created_date.to_datetime_string()}"' +
                  f' eisen={",".join(e.for_notion() for e in inbox_task.eisen)}' +
                  f' difficulty={inbox_task.difficulty.for_notion() if inbox_task.difficulty else ""}')
        else:
            all_projects = projects_repository.list_all_projects(filter_keys=project_keys)
            # Print a summary of all tasks
            for inbox_task in \
                    inbox_tasks_repository\
                            .list_all_inbox_tasks(filter_project_ref_id=(p.ref_id for p in all_projects)):
                big_plan = None
                recurring_task = None
                if inbox_task.big_plan_ref_id:
                    big_plan = big_plans_repository.load_big_plan_by_id(inbox_task.big_plan_ref_id)
                elif inbox_task.recurring_task_ref_id:
                    recurring_task = recurring_tasks_repository.load_recurring_task_by_id(
                        inbox_task.recurring_task_ref_id)
                print(f'id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      (f' big_plan="{big_plan.name}"' if big_plan else "") +
                      (f' recurring_task="{recurring_task.name}"' if recurring_task else "") +
                      f' due_date="{inbox_task.due_date.to_datetime_string() if inbox_task.due_date else ""}"')
