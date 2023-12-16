"""UseCase for creating a metric."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.create import MetricCreateArgs, MetricCreateUseCase


class MetricCreate(LoggedInMutationCommand[MetricCreateUseCase]):
    """UseCase for creating a metric."""

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
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the metric",
        )
        parser.add_argument(
            "--icon",
            dest="icon",
            required=False,
            help="A unicode icon or :alias: for the metric",
        )
        parser.add_argument(
            "--collection-period",
            dest="collection_period",
            required=False,
            choices=RecurringTaskPeriod.all_values(),
            help="The period at which a metric should be recorded",
        )
        parser.add_argument(
            "--collection-eisen",
            dest="collection_eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for collection tasks",
        )
        parser.add_argument(
            "--collection-difficulty",
            dest="collection_difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for collection tasks",
        )
        parser.add_argument(
            "--collection-actionable-from-day",
            type=int,
            dest="collection_actionable_from_day",
            metavar="DAY",
            help="The day of the interval the collection task will be actionable from",
        )
        parser.add_argument(
            "--collection-actionable-from-month",
            type=int,
            dest="collection_actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the collection task will be actionable from",
        )
        parser.add_argument(
            "--collection-due-at-time",
            dest="collection_due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on",
        )
        parser.add_argument(
            "--collection-due-at-day",
            type=int,
            dest="collection_due_at_day",
            metavar="DAY",
            help="The day of the interval the collection task will be due on",
        )
        parser.add_argument(
            "--collection-due-at-month",
            type=int,
            dest="collection_due_at_month",
            metavar="MONTH",
            help="The month of the interval the collection task will be due on",
        )
        parser.add_argument(
            "--unit",
            dest="metric_unit",
            required=False,
            choices=MetricUnit.all_values(),
            help="The unit for the values of the metric",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        name = MetricName.from_raw(args.name)
        icon = EntityIcon.from_raw(args.icon) if args.icon else None
        collection_period = (
            RecurringTaskPeriod.from_raw(args.collection_period)
            if args.collection_period
            else None
        )
        collection_eisen = (
            Eisen.from_raw(args.collection_eisen) if args.collection_eisen else None
        )
        collection_difficulty = (
            Difficulty.from_raw(args.collection_difficulty)
            if args.collection_difficulty
            else None
        )
        collection_actionable_from_day = (
            RecurringTaskDueAtDay.from_raw(
                collection_period,
                args.collection_actionable_from_day,
            )
            if args.collection_actionable_from_day and collection_period
            else None
        )
        collection_actionable_from_month = (
            RecurringTaskDueAtMonth.from_raw(
                collection_period,
                args.collection_actionable_from_month,
            )
            if args.collection_actionable_from_month and collection_period
            else None
        )
        collection_due_at_time = (
            RecurringTaskDueAtTime.from_raw(args.collection_due_at_time)
            if args.collection_due_at_time and collection_period
            else None
        )
        collection_due_at_day = (
            RecurringTaskDueAtDay.from_raw(
                collection_period,
                args.collection_due_at_day,
            )
            if args.collection_due_at_day and collection_period
            else None
        )
        collection_due_at_month = (
            RecurringTaskDueAtMonth.from_raw(
                collection_period,
                args.collection_due_at_month,
            )
            if args.collection_due_at_month and collection_period
            else None
        )
        metric_unit = (
            MetricUnit.from_raw(args.metric_unit) if args.metric_unit else None
        )

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricCreateArgs(
                name=name,
                icon=icon,
                collection_period=collection_period,
                collection_eisen=collection_eisen,
                collection_difficulty=collection_difficulty,
                collection_actionable_from_day=collection_actionable_from_day,
                collection_actionable_from_month=collection_actionable_from_month,
                collection_due_at_time=collection_due_at_time,
                collection_due_at_day=collection_due_at_day,
                collection_due_at_month=collection_due_at_month,
                metric_unit=metric_unit,
            ),
        )
