"""Command for setting the deadlines of a recurring task."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from domain.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.common.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.common.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.common.recurring_task_period import RecurringTaskPeriod
from models.framework import EntityId

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetDeadlines(command.Command):
    """Command class for setting the deadlines of a recurring task."""

    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-set-deadlines"

    @staticmethod
    def description() -> str:
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
        ref_id = EntityId.from_raw(args.ref_id)
        due_at_time = RecurringTaskDueAtTime.from_raw(args.due_at_time) \
            if args.due_at_time else None
        due_at_day = \
            RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.YEARLY, args.due_at_day) \
            if args.due_at_day else None
        due_at_month = \
            RecurringTaskDueAtMonth.from_raw(RecurringTaskPeriod.YEARLY, args.due_at_month) \
            if args.due_at_month else None
        self._recurring_tasks_controller.set_recurring_task_deadlines(ref_id, due_at_time, due_at_day, due_at_month)
