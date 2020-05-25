"""Command for setting the deadlines of a recurring task."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.basic import BasicValidator, RecurringTaskPeriod

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetDeadlines(command.Command):
    """Command class for setting the deadlines of a recurring task."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-set-deadlines"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the deadlines of a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the recurring task to modify")
        parser.add_argument("--due-at-time", dest="due_at_time", metavar="HH:MM", help="The time a task will be due on")
        parser.add_argument("--due-at-day", type=int, dest="due_at_day", metavar="DAY",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--due-at-month", type=int, dest="due_at_month", metavar="MONTH",
                            help="The day of the interval the task will be due on")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = self._basic_validator.entity_id_validate_and_clean(args.ref_id)
        due_at_time = self._basic_validator.recurring_task_due_at_time_validate_and_clean(args.due_at_time) \
            if args.due_at_time else None
        due_at_day = \
            self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                RecurringTaskPeriod.YEARLY, args.due_at_day) \
            if args.due_at_day else None
        due_at_month = \
            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                RecurringTaskPeriod.YEARLY, args.due_at_month) \
            if args.due_at_month else None
        self._recurring_tasks_controller.set_recurring_task_deadlines(ref_id, due_at_time, due_at_day, due_at_month)
