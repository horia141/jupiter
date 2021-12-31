"""UseCase for updating a metric's properties."""
from argparse import Namespace, ArgumentParser
from typing import Final, Optional, List

import jupiter.command.command as command
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.update_action import UpdateAction
from jupiter.use_cases.metrics.update import MetricUpdateUseCase


class MetricUpdate(command.Command):
    """UseCase for updating a metric's properties."""

    _command: Final[MetricUpdateUseCase]

    def __init__(self, the_command: MetricUpdateUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a metric"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--metric", dest="metric_key", required=True, help="The key of the metric")
        parser.add_argument("--name", dest="name", required=False, help="The name of the metric")
        collection_project_group = parser.add_mutually_exclusive_group()
        collection_project_group.add_argument(
            "--collection-project", dest="collection_project_key", required=False,
            help="The project key to generate recurring collection tasks")
        collection_project_group.add_argument(
            "--clear-collection-project", dest="clear_collection_project_key",
            required=False, default=False, action="store_const", const=True,
            help="Clear the collection project")
        collection_period_group = parser.add_mutually_exclusive_group()
        collection_period_group.add_argument(
            "--collection-period", dest="collection_period", required=False,
            choices=RecurringTaskPeriod.all_values(),
            help="The period at which a metric should be recorded")
        collection_period_group.add_argument(
            "--clear-collection-period", dest="clear_collection_period", default=False,
            action="store_const", const=True, help="Clear the collection period")
        collection_period_eisen = parser.add_mutually_exclusive_group()
        collection_period_eisen.add_argument(
            "--collection-eisen", dest="collection_eisen", default=[], action="append",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for collection tasks")
        collection_period_eisen.add_argument(
            "--clear-collection-eisen", dest="clear_collection_eisen", default=False,
            action="store_const", const=True, help="Clear the collection eisen")
        collection_period_difficulty = parser.add_mutually_exclusive_group()
        collection_period_difficulty.add_argument("--collection-difficulty", dest="collection_difficulty",
                                                  choices=Difficulty.all_values(),
                                                  help="The difficulty to use for collection tasks")
        collection_period_difficulty.add_argument("--clear-collection-difficulty", dest="clear_collection_difficulty",
                                                  default=False,
                                                  action="store_const", const=True,
                                                  help="Clear the collection difficulty")
        collection_period_actionable_from_day = parser.add_mutually_exclusive_group()
        collection_period_actionable_from_day.add_argument(
            "--collection-actionable-from-day", type=int,
            dest="collection_actionable_from_day",
            metavar="DAY",
            help="The day of the interval the collection task will be actionable from")
        collection_period_actionable_from_day.add_argument(
            "--clear-collection-actionable-from-day",
            dest="clear_collection_actionable_from_day", default=False,
            action="store_const", const=True,
            help="Clear the collection actionable day")
        collection_period_actionable_from_month = parser.add_mutually_exclusive_group()
        collection_period_actionable_from_month.add_argument(
            "--collection-actionable-from-month", type=int,
            dest="collection_actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the collection task will be actionable from")
        collection_period_actionable_from_month.add_argument(
            "--clear-collection-actionable-from-month",
            dest="clear_collection_actionable_from_month",
            default=False,
            action="store_const", const=True,
            help="Clear the collection actionable month")
        collection_period_due_at_time = parser.add_mutually_exclusive_group()
        collection_period_due_at_time.add_argument(
            "--collection-due-at-time", dest="collection_due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on")
        collection_period_due_at_time.add_argument(
            "--clear-collection-due-at-time",
            dest="clear_collection_due_at_time",
            default=False,
            action="store_const", const=True,
            help="Clear the collection due time")
        collection_period_due_at_day = parser.add_mutually_exclusive_group()
        collection_period_due_at_day.add_argument(
            "--collection-due-at-day", type=int, dest="collection_due_at_day",
            metavar="DAY",
            help="The day of the interval the collection task will be due on")
        collection_period_due_at_day.add_argument(
            "--clear-collection-due-at-day", dest="clear_collection_due_at_day",
            default=False,
            action="store_const", const=True, help="Clear the collection due day")
        collection_period_due_at_month = parser.add_mutually_exclusive_group()
        collection_period_due_at_month.add_argument(
            "--collection-due-at-month", type=int,
            dest="collection_due_at_month", metavar="MONTH",
            help="The month of the interval the collection task will be due on")
        collection_period_due_at_month.add_argument(
            "--clear-collection-due-at-month",
            dest="clear_collection_due_at_month",
            default=False,
            action="store_const", const=True,
            help="Clear the collection due month")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        metric_key = MetricKey.from_raw(args.metric_key)
        if args.name is not None:
            name = UpdateAction.change_to(MetricName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        collection_project_key: UpdateAction[Optional[ProjectKey]]
        if args.clear_collection_project_key:
            collection_project_key = UpdateAction.change_to(None)
        elif args.collection_project_key is not None:
            collection_project_key = UpdateAction.change_to(ProjectKey.from_raw(args.collection_project_key))
        else:
            collection_project_key = UpdateAction.do_nothing()
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]
        if args.clear_collection_period:
            collection_period = UpdateAction.change_to(None)
        elif args.collection_period is not None:
            collection_period = UpdateAction.change_to(
                RecurringTaskPeriod.from_raw(args.collection_period))
        else:
            collection_period = UpdateAction.do_nothing()
        collection_eisen: UpdateAction[List[Eisen]]
        if args.clear_collection_eisen:
            collection_eisen = UpdateAction.change_to([])
        elif len(args.collection_eisen) > 0:
            collection_eisen = UpdateAction.change_to(
                [Eisen.from_raw(e) for e in args.collection_eisen])
        else:
            collection_eisen = UpdateAction.do_nothing()
        collection_difficulty: UpdateAction[Optional[Difficulty]]
        if args.clear_collection_difficulty:
            collection_difficulty = UpdateAction.change_to(None)
        elif args.collection_difficulty is not None:
            collection_difficulty = UpdateAction.change_to(
                Difficulty.from_raw(args.collection_difficulty))
        else:
            collection_difficulty = UpdateAction.do_nothing()
        collection_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_collection_actionable_from_day:
            collection_actionable_from_day = UpdateAction.change_to(None)
        elif args.collection_actionable_from_day is not None:
            collection_actionable_from_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.YEARLY, args.collection_actionable_from_day))
        else:
            collection_actionable_from_day = UpdateAction.do_nothing()
        collection_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_collection_actionable_from_month:
            collection_actionable_from_month = UpdateAction.change_to(None)
        elif args.collection_actionable_from_month is not None:
            collection_actionable_from_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY, args.collection_actionable_from_month))
        else:
            collection_actionable_from_month = UpdateAction.do_nothing()
        collection_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        if args.clear_collection_due_at_time:
            collection_due_at_time = UpdateAction.change_to(None)
        elif args.collection_due_at_time is not None:
            collection_due_at_time = \
                UpdateAction.change_to(RecurringTaskDueAtTime.from_raw(args.collection_due_at_time))
        else:
            collection_due_at_time = UpdateAction.do_nothing()
        collection_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_collection_due_at_day:
            collection_due_at_day = UpdateAction.change_to(None)
        elif args.collection_due_at_day is not None:
            collection_due_at_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.YEARLY, args.collection_due_at_day))
        else:
            collection_due_at_day = UpdateAction.do_nothing()
        collection_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_collection_due_at_month:
            collection_due_at_month = UpdateAction.change_to(None)
        elif args.collection_due_at_month is not None:
            collection_due_at_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY, args.collection_due_at_month))
        else:
            collection_due_at_month = UpdateAction.do_nothing()
        self._command.execute(
            MetricUpdateUseCase.Args(
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
                collection_due_at_month=collection_due_at_month))
