"""Command for showing the recurring tasks."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class RecurringTasksShow(command.Command):
    """Command class for showing the recurring tasks."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the list of recurring tasks"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_ids", default=[], action="append",
                            help="The id of the vacations to modify")
        parser.add_argument("--project", type=str, dest="project_keys", default=[], action="append",
                            help="Allow only tasks from this project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_ids = [self._basic_validator.entity_id_validate_and_clean(rid) for rid in args.ref_ids] \
            if len(args.ref_ids) > 0 else None
        project_keys = [self._basic_validator.project_key_validate_and_clean(p) for p in args.project_keys] \
            if len(args.project_keys) > 0 else None
        response = self._recurring_tasks_controller.load_all_recurring_tasks(
            filter_ref_ids=ref_ids, filter_project_keys=project_keys)

        for recurring_task_entry in response.recurring_tasks:
            recurring_task = recurring_task_entry.recurring_task
            inbox_tasks = recurring_task_entry.inbox_tasks
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
            print("  Tasks:")

            for inbox_task in inbox_tasks:
                print(f'   - id={inbox_task.ref_id} {inbox_task.name}' +
                      f' status={inbox_task.status.value}' +
                      f' archived="{inbox_task.archived}"' +
                      f' due_date="{inbox_task.due_date.to_datetime_string() if inbox_task.due_date else ""}"')
