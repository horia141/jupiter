"""Command for setting the actionable date config of a recurring task."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.framework import EntityId
from models.basic import BasicValidator, RecurringTaskPeriod

LOGGER = logging.getLogger(__name__)


class RecurringTasksSetActionableConfig(command.Command):
    """Command class for setting the actionable config of a recurring task."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-set-actionable-config"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the actionable config of a recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--id", type=str, dest="ref_id", required=True,
                            help="The id of the recurring task to modify")
        parser.add_argument("--actionable-from-day", type=int, dest="actionable_from_day", metavar="DAY",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--actionable-from-month", type=int, dest="actionable_from_month", metavar="MONTH",
                            help="The day of the interval the task will be due on")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        actionable_from_day = \
            self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                RecurringTaskPeriod.YEARLY, args.actionable_from_day) \
            if args.actionable_from_day else None
        actionable_from_month = \
            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                RecurringTaskPeriod.YEARLY, args.actionable_from_month) \
            if args.actionable_from_month else None
        self._recurring_tasks_controller.set_recurring_task_actionable_config(
            ref_id, actionable_from_day, actionable_from_month)
