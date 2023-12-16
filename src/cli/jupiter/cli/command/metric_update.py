"""UseCase for updating a metric's properties."""
from argparse import ArgumentParser, Namespace
from typing import Optional

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
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.metrics.update import MetricUpdateArgs, MetricUpdateUseCase


class MetricUpdate(LoggedInMutationCommand[MetricUpdateUseCase]):
    """UseCase for updating a metric's properties."""

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
        parser.add_argument(
            "--id",
            dest="ref_id",
            required=True,
            help="The key of the metric",
        )
        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            help="The name of the metric",
        )
        icon = parser.add_mutually_exclusive_group()
        icon.add_argument(
            "--icon",
            dest="icon",
            help="The icon or :alias: for the metric",
        )
        icon.add_argument(
            "--clear-icon",
            dest="clear_icon",
            default=False,
            action="store_const",
            const=True,
            help="Clear the icon and use the default one",
        )
        collection_period_group = parser.add_mutually_exclusive_group()
        collection_period_group.add_argument(
            "--collection-period",
            dest="collection_period",
            required=False,
            choices=RecurringTaskPeriod.all_values(),
            help="The period at which a metric should be recorded",
        )
        collection_period_group.add_argument(
            "--clear-collection-period",
            dest="clear_collection_period",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection period",
        )
        collection_eisen = parser.add_mutually_exclusive_group()
        collection_eisen.add_argument(
            "--collection-eisen",
            dest="collection_eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for collection task",
        )
        collection_eisen.add_argument(
            "--clear-collection-eisen",
            dest="clear_collection_eisen",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection eisen of the metric",
        )
        collection_period_difficulty = parser.add_mutually_exclusive_group()
        collection_period_difficulty.add_argument(
            "--collection-difficulty",
            dest="collection_difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for collection tasks",
        )
        collection_period_difficulty.add_argument(
            "--clear-collection-difficulty",
            dest="clear_collection_difficulty",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection difficulty",
        )
        collection_period_actionable_from_day = parser.add_mutually_exclusive_group()
        collection_period_actionable_from_day.add_argument(
            "--collection-actionable-from-day",
            type=int,
            dest="collection_actionable_from_day",
            metavar="DAY",
            help="The day of the interval the collection task will be actionable from",
        )
        collection_period_actionable_from_day.add_argument(
            "--clear-collection-actionable-from-day",
            dest="clear_collection_actionable_from_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection actionable day",
        )
        collection_period_actionable_from_month = parser.add_mutually_exclusive_group()
        collection_period_actionable_from_month.add_argument(
            "--collection-actionable-from-month",
            type=int,
            dest="collection_actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the collection task will be actionable from",
        )
        collection_period_actionable_from_month.add_argument(
            "--clear-collection-actionable-from-month",
            dest="clear_collection_actionable_from_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection actionable month",
        )
        collection_period_due_at_time = parser.add_mutually_exclusive_group()
        collection_period_due_at_time.add_argument(
            "--collection-due-at-time",
            dest="collection_due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on",
        )
        collection_period_due_at_time.add_argument(
            "--clear-collection-due-at-time",
            dest="clear_collection_due_at_time",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection due time",
        )
        collection_period_due_at_day = parser.add_mutually_exclusive_group()
        collection_period_due_at_day.add_argument(
            "--collection-due-at-day",
            type=int,
            dest="collection_due_at_day",
            metavar="DAY",
            help="The day of the interval the collection task will be due on",
        )
        collection_period_due_at_day.add_argument(
            "--clear-collection-due-at-day",
            dest="clear_collection_due_at_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection due day",
        )
        collection_period_due_at_month = parser.add_mutually_exclusive_group()
        collection_period_due_at_month.add_argument(
            "--collection-due-at-month",
            type=int,
            dest="collection_due_at_month",
            metavar="MONTH",
            help="The month of the interval the collection task will be due on",
        )
        collection_period_due_at_month.add_argument(
            "--clear-collection-due-at-month",
            dest="clear_collection_due_at_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection due month",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name is not None:
            name = UpdateAction.change_to(MetricName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        icon: UpdateAction[Optional[EntityIcon]]
        if args.clear_icon:
            icon = UpdateAction.change_to(None)
        elif args.icon:
            icon = UpdateAction.change_to(EntityIcon.from_raw(args.icon))
        else:
            icon = UpdateAction.do_nothing()
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]
        if args.clear_collection_period:
            collection_period = UpdateAction.change_to(None)
        elif args.collection_period is not None:
            collection_period = UpdateAction.change_to(
                RecurringTaskPeriod.from_raw(args.collection_period),
            )
        else:
            collection_period = UpdateAction.do_nothing()
        collection_eisen: UpdateAction[Optional[Eisen]]
        if args.clear_collection_eisen:
            collection_eisen = UpdateAction.change_to(None)
        elif args.collection_eisen:
            collection_eisen = UpdateAction.change_to(Eisen.from_raw(args.eisen))
        else:
            collection_eisen = UpdateAction.do_nothing()
        collection_difficulty: UpdateAction[Optional[Difficulty]]
        if args.clear_collection_difficulty:
            collection_difficulty = UpdateAction.change_to(None)
        elif args.collection_difficulty is not None:
            collection_difficulty = UpdateAction.change_to(
                Difficulty.from_raw(args.collection_difficulty),
            )
        else:
            collection_difficulty = UpdateAction.do_nothing()
        collection_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_collection_actionable_from_day:
            collection_actionable_from_day = UpdateAction.change_to(None)
        elif args.collection_actionable_from_day is not None:
            collection_actionable_from_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.collection_actionable_from_day,
                ),
            )
        else:
            collection_actionable_from_day = UpdateAction.do_nothing()
        collection_actionable_from_month: UpdateAction[
            Optional[RecurringTaskDueAtMonth]
        ]
        if args.clear_collection_actionable_from_month:
            collection_actionable_from_month = UpdateAction.change_to(None)
        elif args.collection_actionable_from_month is not None:
            collection_actionable_from_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.collection_actionable_from_month,
                ),
            )
        else:
            collection_actionable_from_month = UpdateAction.do_nothing()
        collection_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        if args.clear_collection_due_at_time:
            collection_due_at_time = UpdateAction.change_to(None)
        elif args.collection_due_at_time is not None:
            collection_due_at_time = UpdateAction.change_to(
                RecurringTaskDueAtTime.from_raw(args.collection_due_at_time),
            )
        else:
            collection_due_at_time = UpdateAction.do_nothing()
        collection_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_collection_due_at_day:
            collection_due_at_day = UpdateAction.change_to(None)
        elif args.collection_due_at_day is not None:
            collection_due_at_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.collection_due_at_day,
                ),
            )
        else:
            collection_due_at_day = UpdateAction.do_nothing()
        collection_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_collection_due_at_month:
            collection_due_at_month = UpdateAction.change_to(None)
        elif args.collection_due_at_month is not None:
            collection_due_at_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    RecurringTaskPeriod.YEARLY,
                    args.collection_due_at_month,
                ),
            )
        else:
            collection_due_at_month = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            MetricUpdateArgs(
                ref_id=ref_id,
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
            ),
        )
