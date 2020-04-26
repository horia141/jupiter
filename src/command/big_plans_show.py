"""Command for showing the big plans."""

import logging

import command.command as command
import repository.big_plans as big_plans
import repository.inbox_tasks as inbox_tasks
import repository.projects as projects
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class BigPlansShow(command.Command):
    """Command class for showing the big plans."""

    @staticmethod
    def name():
        """The name of the command."""
        return "big-plans-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the list of big plans"

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
        project_keys = [basic_validator.project_key_validate_and_clean(pk) for pk in args.project_keys]\
            if len(args.project_keys) > 0 else None

        # Load local storage

        projects_repository = projects.ProjectsRepository()
        inbox_tasks_repository = inbox_tasks.InboxTasksRepository()
        big_plans_repository = big_plans.BigPlansRepository()

        # Dump out contents of the recurring tasks

        if ref_id:
            # Print details about a single task
            big_plan = big_plans_repository.load_big_plan_by_id(ref_id)
            associated_inbox_tasks = inbox_tasks_repository.list_all_inbox_tasks(
                filter_big_plan_ref_id=[big_plan.ref_id])
            print(f'id={big_plan.ref_id} {big_plan.name}' +
                  f' status={big_plan.status.value}' +
                  f' archived="{big_plan.archived}"' +
                  f' due_date="{big_plan.due_date.to_datetime_string() if big_plan.due_date else ""}"')
            print("  Tasks:")
            for inbox_task in associated_inbox_tasks:
                print(f'   - id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      f' due_date="{inbox_task.due_date.to_datetime_string() if inbox_task.due_date else ""}"')
        else:
            all_projects = projects_repository.list_all_projects(filter_keys=project_keys)
            # Print a summary of all tasks
            for big_plan in \
                    big_plans_repository\
                            .list_all_big_plans(filter_project_ref_id=(p.ref_id for p in all_projects)):
                print(f'id={big_plan.ref_id} {big_plan.name}' +
                      f' status={big_plan.status.value}' +
                      f' archived="{big_plan.archived}"' +
                      f' due_date="{big_plan.due_date.to_datetime_string() if big_plan.due_date else ""}"')
