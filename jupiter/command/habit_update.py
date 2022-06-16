"""UseCase for updating a habit."""
import logging
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

from jupiter.command import command
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.use_cases.habits.update import HabitUpdateUseCase
from jupiter.utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class HabitUpdate(command.Command):
    """UseCase class for creating a habit."""

    _global_properties: Final[GlobalProperties]
    _command: Final[HabitUpdateUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: HabitUpdateUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "habit-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a habit"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the habit to modify",
        )
        parser.add_argument("--name", dest="name", help="The name of the habit")
        parser.add_argument(
            "--period",
            dest="period",
            choices=RecurringTaskPeriod.all_values(),
            help="The period for the habit",
        )
        parser.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for task",
        )
        difficulty = parser.add_mutually_exclusive_group()
        difficulty.add_argument(
            "--difficulty",
            dest="difficulty",
            choices=Difficulty.all_values(),
            help="The difficulty to use for tasks",
        )
        difficulty.add_argument(
            "--clear-difficulty",
            dest="clear_difficulty",
            default=False,
            action="store_const",
            const=True,
            help="Clear the difficulty  of the habit",
        )
        actionable_from_day = parser.add_mutually_exclusive_group()
        actionable_from_day.add_argument(
            "--actionable-from-day",
            type=int,
            dest="actionable_from_day",
            metavar="DAY",
            help="The day of the interval the task will be actionable from",
        )
        actionable_from_day.add_argument(
            "--clear-actionable-from-day",
            dest="clear_actionable_from_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the actionable day of the habit",
        )
        actionable_from_month = parser.add_mutually_exclusive_group()
        actionable_from_month.add_argument(
            "--actionable-from-month",
            type=int,
            dest="actionable_from_month",
            metavar="MONTH",
            help="The month of the interval the task will be actionable from",
        )
        actionable_from_month.add_argument(
            "--clear-actionable-from-month",
            dest="clear_actionable_from_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the actionable month of the habit",
        )
        due_at_time = parser.add_mutually_exclusive_group()
        due_at_time.add_argument(
            "--due-at-time",
            dest="due_at_time",
            metavar="HH:MM",
            help="The time a task will be due on",
        )
        due_at_time.add_argument(
            "--clear-due-at-time",
            dest="clear_due_at_time",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due time of the habit",
        )
        due_at_day = parser.add_mutually_exclusive_group()
        due_at_day.add_argument(
            "--due-at-day",
            type=int,
            dest="due_at_day",
            metavar="DAY",
            help="The day of the interval the task will be due on",
        )
        due_at_day.add_argument(
            "--clear-due-at-day",
            dest="clear_due_at_day",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due day of the habit",
        )
        due_at_month = parser.add_mutually_exclusive_group()
        due_at_month.add_argument(
            "--due-at-month",
            type=int,
            dest="due_at_month",
            metavar="MONTH",
            help="The month of the interval the task will be due on",
        )
        due_at_month.add_argument(
            "--clear-due-at-month",
            dest="clear_due_at_month",
            default=False,
            action="store_const",
            const=True,
            help="Clear the due month of the habit",
        )
        must_do = parser.add_mutually_exclusive_group()
        must_do.add_argument(
            "--can-skip",
            dest="can_skip",
            default=False,
            action="store_true",
            help="Treat this task as skippable in a vacation",
        )
        skip_rule = parser.add_mutually_exclusive_group()
        skip_rule.add_argument(
            "--skip-rule", dest="skip_rule", help="The skip rule for the task"
        )
        skip_rule.add_argument(
            "--clear-skip-rule",
            dest="clear_skip_rule",
            default=False,
            action="store_const",
            const=True,
            help="Clear the skip rule of the habit",
        )
        repeats_in_period_count = parser.add_mutually_exclusive_group()
        repeats_in_period_count.add_argument(
            "--repeats-in-period",
            dest="repeats_in_period_count",
            type=int,
            help="THow many times should the task repeat in the period",
        )
        repeats_in_period_count.add_argument(
            "--clear-repeats-in-period",
            dest="clear_repeats_in_period_count",
            default=False,
            action="store_const",
            const=True,
            help="Clear the repeats in period parameter",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(HabitName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.period:
            period = UpdateAction.change_to(RecurringTaskPeriod.from_raw(args.period))
        else:
            period = UpdateAction.do_nothing()
        if args.eisen:
            eisen = UpdateAction.change_to(Eisen.from_raw(args.eisen))
        else:
            eisen = UpdateAction.do_nothing()
        difficulty: UpdateAction[Optional[Difficulty]]
        if args.clear_difficulty:
            difficulty = UpdateAction.change_to(None)
        elif args.difficulty:
            difficulty = UpdateAction.change_to(Difficulty.from_raw(args.difficulty))
        else:
            difficulty = UpdateAction.do_nothing()
        actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_actionable_from_day:
            actionable_from_day = UpdateAction.change_to(None)
        elif args.actionable_from_day:
            actionable_from_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    period.value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.actionable_from_day,
                )
            )
        else:
            actionable_from_day = UpdateAction.do_nothing()
        actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_actionable_from_month:
            actionable_from_month = UpdateAction.change_to(None)
        elif args.actionable_from_month:
            actionable_from_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    period.value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.actionable_from_month,
                )
            )
        else:
            actionable_from_month = UpdateAction.do_nothing()
        due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        if args.clear_due_at_time:
            due_at_time = UpdateAction.change_to(None)
        elif args.due_at_time:
            due_at_time = UpdateAction.change_to(
                RecurringTaskDueAtTime.from_raw(args.due_at_time)
            )
        else:
            due_at_time = UpdateAction.do_nothing()
        due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_due_at_day:
            due_at_day = UpdateAction.change_to(None)
        elif args.due_at_day:
            due_at_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    period.value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.due_at_day,
                )
            )
        else:
            due_at_day = UpdateAction.do_nothing()
        due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_due_at_month:
            due_at_month = UpdateAction.change_to(None)
        elif args.due_at_month:
            due_at_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    period.value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.due_at_month,
                )
            )
        else:
            due_at_month = UpdateAction.do_nothing()
        skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]]
        if args.clear_skip_rule:
            skip_rule = UpdateAction.change_to(None)
        elif args.skip_rule:
            skip_rule = UpdateAction.change_to(
                RecurringTaskSkipRule.from_raw(args.skip_rule)
            )
        else:
            skip_rule = UpdateAction.do_nothing()
        repeats_in_period_count: UpdateAction[Optional[int]]
        if args.clear_repeats_in_period_count:
            repeats_in_period_count = UpdateAction.change_to(None)
        elif args.repeats_in_period_count:
            repeats_in_period_count = UpdateAction.change_to(
                args.repeats_in_period_count
            )
        else:
            repeats_in_period_count = UpdateAction.do_nothing()
        self._command.execute(
            HabitUpdateUseCase.Args(
                ref_id=ref_id,
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
