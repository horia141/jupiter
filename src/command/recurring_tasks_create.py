"""Command for adding a recurring task."""

import logging
from argparse import Namespace, ArgumentParser
from typing import Final

import command.command as command
from controllers.recurring_tasks import RecurringTasksController
from models.basic import BasicValidator, RecurringTaskType

LOGGER = logging.getLogger(__name__)


class RecurringTasksCreate(command.Command):
    """Command class for creating a recurring task."""

    _basic_validator: Final[BasicValidator]
    _recurring_tasks_controller: Final[RecurringTasksController]

    def __init__(self, basic_validator: BasicValidator, recurring_tasks_controller: RecurringTasksController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._recurring_tasks_controller = recurring_tasks_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "recurring-tasks-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new recurring task"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--project", dest="project_key", required=True, help="The project key to add the task to")
        parser.add_argument("--name", dest="name", required=True, help="The name of the recurring task")
        parser.add_argument("--group", dest="group", required=True, help="The group for the recurring task")
        parser.add_argument("--period", dest="period", choices=BasicValidator.recurring_task_period_values(),
                            required=True, help="The period for the recurring task")
        parser.add_argument("--type", dest="the_type", choices=BasicValidator.recurring_task_type_values(),
                            default=RecurringTaskType.CHORE.value, required=True,
                            help="The type of the recurring task")
        parser.add_argument("--eisen", dest="eisen", default=[], action="append",
                            choices=BasicValidator.eisen_values(), help="The Eisenhower matrix values to use for task")
        parser.add_argument("--difficulty", dest="difficulty", choices=BasicValidator.difficulty_values(),
                            help="The difficulty to use for tasks")
        parser.add_argument("--due-at-time", dest="due_at_time", metavar="HH:MM", help="The time a task will be due on")
        parser.add_argument("--due-at-day", type=int, dest="due_at_day", metavar="DAY",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--due-at-month", type=int, dest="due_at_month", metavar="MONTH",
                            help="The day of the interval the task will be due on")
        parser.add_argument("--must-do", dest="must_do", default=False, action="store_true",
                            help="Whether to treat this task as must do or not")
        parser.add_argument("--skip-rule", dest="skip_rule", help="The skip rule for the task")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = self._basic_validator.project_key_validate_and_clean(args.project_key)
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        group = self._basic_validator.entity_name_validate_and_clean(args.group)
        period = self._basic_validator.recurring_task_period_validate_and_clean(args.period)
        the_type = self._basic_validator.recurring_task_type_validate_and_clean(args.the_type)
        eisen = [self._basic_validator.eisen_validate_and_clean(e) for e in args.eisen]
        difficulty = self._basic_validator.difficulty_validate_and_clean(args.difficulty) if args.difficulty else None
        due_at_time = self._basic_validator.recurring_task_due_at_time_validate_and_clean(args.due_at_time)\
            if args.due_at_time else None
        due_at_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(period, args.due_at_day) \
            if args.due_at_day else None
        due_at_month = self._basic_validator.recurring_task_due_at_month_validate_and_clean(period, args.due_at_month) \
            if args.due_at_month else None
        must_do = args.must_do
        skip_rule = self._basic_validator.recurring_task_skip_rule_validate_and_clean(args.skip_rule) \
            if args.skip_rule else None
        self._recurring_tasks_controller.create_recurring_task(
            project_key=project_key,
            name=name,
            group=group,
            period=period,
            the_type=the_type,
            eisen=eisen,
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule)
