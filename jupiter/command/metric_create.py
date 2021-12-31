"""UseCase for creating a metric."""
from argparse import Namespace, ArgumentParser
from typing import Final

import jupiter.command.command as command
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.use_cases.metrics.create import MetricCreateUseCase


class MetricCreate(command.Command):
    """UseCase for creating a metric."""

    _command: Final[MetricCreateUseCase]

    def __init__(self, the_command: MetricCreateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-create"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Create a new metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--name", dest="name", required=True, help="The name of the metric")
        parser.add_argument("--collection-project", dest="collection_project_key", required=False,
                            help="The project key to generate recurring collection tasks")
        parser.add_argument("--collection-period", dest="collection_period", required=False,
                            choices=RecurringTaskPeriod.all_values(),
                            help="The period at which a metric should be recorded")
        parser.add_argument("--collection-eisen", dest="collection_eisen", default=[], action="append",
                            choices=Eisen.all_values(),
                            help="The Eisenhower matrix values to use for collection tasks")
        parser.add_argument("--collection-difficulty", dest="collection_difficulty",
                            choices=Difficulty.all_values(),
                            help="The difficulty to use for collection tasks")
        parser.add_argument("--collection-actionable-from-day", type=int,
                            dest="collection_actionable_from_day", metavar="DAY",
                            help="The day of the interval the collection task will be actionable from")
        parser.add_argument("--collection-actionable-from-month", type=int,
                            dest="collection_actionable_from_month", metavar="MONTH",
                            help="The month of the interval the collection task will be actionable from")
        parser.add_argument("--collection-due-at-time", dest="collection_due_at_time",
                            metavar="HH:MM", help="The time a task will be due on")
        parser.add_argument("--collection-due-at-day", type=int, dest="collection_due_at_day", metavar="DAY",
                            help="The day of the interval the collection task will be due on")
        parser.add_argument("--collection-due-at-month", type=int, dest="collection_due_at_month", metavar="MONTH",
                            help="The month of the interval the collection task will be due on")
        parser.add_argument("--unit", dest="metric_unit", required=False,
                            choices=MetricUnit.all_values(),
                            help="The unit for the values of the metric")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = MetricKey.from_raw(args.metric_key)
        name = MetricName.from_raw(args.name)
        collection_project_key = ProjectKey.from_raw(args.collection_project_key) \
            if args.collection_project_key else None
        collection_period = RecurringTaskPeriod.from_raw(args.collection_period)\
            if args.collection_period else None
        collection_eisen = [Eisen.from_raw(e) for e in args.collection_eisen]
        collection_difficulty = Difficulty.from_raw(args.collection_difficulty) \
            if args.collection_difficulty else None
        collection_actionable_from_day = RecurringTaskDueAtDay.from_raw(
            collection_period, args.collection_actionable_from_day) \
            if args.collection_actionable_from_day and collection_period else None
        collection_actionable_from_month = RecurringTaskDueAtMonth.from_raw(
            collection_period, args.collection_actionable_from_month) \
            if args.collection_actionable_from_month and collection_period else None
        collection_due_at_time = \
            RecurringTaskDueAtTime.from_raw(args.collection_due_at_time) \
            if args.collection_due_at_time and collection_period else None
        collection_due_at_day = \
            RecurringTaskDueAtDay.from_raw(collection_period, args.collection_due_at_day) \
            if args.collection_due_at_day and collection_period else None
        collection_due_at_month = \
            RecurringTaskDueAtMonth.from_raw(collection_period, args.collection_due_at_month) \
            if args.collection_due_at_month and collection_period else None
        metric_unit = MetricUnit.from_raw(args.metric_unit) if args.metric_unit else None
        self._command.execute(MetricCreateUseCase.Args(
            key=metric_key,
            name=name,
            collection_project_key=collection_project_key,
            collection_period=collection_period,
            collection_eisen=collection_eisen,
            collection_difficulty=collection_difficulty,
            collection_actionable_from_day=collection_actionable_from_day,
            collection_actionable_from_month=collection_actionable_from_month,
            collection_due_at_time=collection_due_at_time,
            collection_due_at_day=collection_due_at_day,
            collection_due_at_month=collection_due_at_month,
            metric_unit=metric_unit))
