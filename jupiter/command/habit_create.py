"""UseCase for adding a habit."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final

from jupiter.command import command
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.use_cases.habits.create import HabitCreateUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class HabitCreate(command.Command):
    """UseCase class for creating a habit."""

    _global_properties: Final[GlobalProperties]
    _command: Final[HabitCreateUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: HabitCreateUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "habit-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new habit"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--project",
            dest="project_key",
            required=False,
            help="The project key to add the task to",
        )
        parser.add_argument(
            "--name", dest="name", required=True, help="The name of the habit"
        )
        parser.add_argument(
            "--period",
            dest="period",
            choices=RecurringTaskPeriod.all_values(),
            required=True,
            help="The period for the habit",
        )
        parser.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for task",
        )
        parser.add_argument(
            "--difficulty",
            dest="difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for tasks",
        )
        parser.add_argument(
            "--actionable-from-day",
            type=int,
            dest="actionable_from_day",
            metavar="DAY",
            help="The day of the interval the task will be actionable from",
        )
        parser.add_argument(
            "--actionable-from-month",
            type=int,
            dest="actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the task will be actionable from",
        )
        parser.add_argument(
            "--due-at-time",
            dest="due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on",
        )
        parser.add_argument(
            "--due-at-day",
            type=int,
            dest="due_at_day",
            metavar="DAY",
            help="The day of the interval the task will be due on",
        )
        parser.add_argument(
            "--due-at-month",
            type=int,
            dest="due_at_month",
            metavar="MONTH",
            help="The month of the interval the task will be due on",
        )
        parser.add_argument(
            "--start-at-date",
            dest="start_at_date",
            help="The date from which tasks should be generated",
        )
        parser.add_argument(
            "--skip-rule", dest="skip_rule", help="The skip rule for the task"
        )
        parser.add_argument(
            "--repeats-in-period",
            dest="repeats_in_period_count",
            type=int,
            help="How many times should the task repeat in the period",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        project_key = (
            ProjectKey.from_raw(args.project_key) if args.project_key else None
        )
        name = HabitName.from_raw(args.name)
        period = RecurringTaskPeriod.from_raw(args.period)
        eisen = Eisen.from_raw(args.eisen) if args.eisen else None
        difficulty = Difficulty.from_raw(args.difficulty) if args.difficulty else None
        actionable_from_day = (
            RecurringTaskDueAtDay.from_raw(period, args.actionable_from_day)
            if args.actionable_from_day
            else None
        )
        actionable_from_month = (
            RecurringTaskDueAtMonth.from_raw(period, args.actionable_from_month)
            if args.actionable_from_month
            else None
        )
        due_at_time = (
            RecurringTaskDueAtTime.from_raw(args.due_at_time)
            if args.due_at_time
            else None
        )
        due_at_day = (
            RecurringTaskDueAtDay.from_raw(period, args.due_at_day)
            if args.due_at_day
            else None
        )
        due_at_month = (
            RecurringTaskDueAtMonth.from_raw(period, args.due_at_month)
            if args.due_at_month
            else None
        )
        skip_rule = (
            RecurringTaskSkipRule.from_raw(args.skip_rule) if args.skip_rule else None
        )
        repeats_in_period_count = args.repeats_in_period_count
        self._command.execute(
            HabitCreateUseCase.Args(
                project_key=project_key,
                name=name,
                period=period,
                eisen=eisen,
                difficulty=difficulty,
                actionable_from_day=actionable_from_day,
                actionable_from_month=actionable_from_month,
                due_at_time=due_at_time,
                due_at_day=due_at_day,
                due_at_month=due_at_month,
                skip_rule=skip_rule,
                repeats_in_period_count=repeats_in_period_count,
            )
        )
