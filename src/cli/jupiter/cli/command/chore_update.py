"""UseCase for updating a chore."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.use_cases.chores.update import ChoreUpdateArgs, ChoreUpdateUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties


class ChoreUpdate(LoggedInMutationCommand[ChoreUpdateUseCase]):
    """UseCase class for creating a chore."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: ChoreUpdateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "chore-update"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update a chore"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--id",
            type=str,
            dest="ref_id",
            required=True,
            help="The id of the chore to modify",
        )
        parser.add_argument("--name", dest="name", help="The name of the chore")
        parser.add_argument(
            "--period",
            dest="period",
            choices=RecurringTaskPeriod.all_values(),
            help="The period for the chore",
        )
        eisen = parser.add_mutually_exclusive_group()
        eisen.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for task",
        )
        eisen.add_argument(
            "--clear-eisen",
            dest="clear_eisen",
            default=False,
            action="store_const",
            const=True,
            help="Clear the eisen of the chore",
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
            help="Clear the difficulty  of the chore",
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
            help="Clear the actionable day of the chore",
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
            help="Clear the actionable month of the chore",
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
            help="Clear the due time of the chore",
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
            help="Clear the due day of the chore",
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
            help="Clear the due month of the chore",
        )
        parser.add_argument(
            "--start-at-date",
            dest="start_at_date",
            help="The date from which tasks should be generated",
        )
        end_at_date = parser.add_mutually_exclusive_group()
        end_at_date.add_argument(
            "--end-at-date",
            dest="end_at_date",
            help="The date until which tasks should be generated",
        )
        end_at_date.add_argument(
            "--clear-end-at-date",
            dest="clear_end_at_date",
            default=False,
            action="store_const",
            const=True,
            help="Clear the end date of the chore",
        )
        must_do = parser.add_mutually_exclusive_group()
        must_do.add_argument(
            "--must-do",
            dest="must_do",
            default=False,
            action="store_true",
            help="Treat this task as must do in a vacation",
        )
        must_do.add_argument(
            "--can-skip",
            dest="can_skip",
            default=False,
            action="store_true",
            help="Treat this task as skippable in a vacation",
        )
        skip_rule = parser.add_mutually_exclusive_group()
        skip_rule.add_argument(
            "--skip-rule",
            dest="skip_rule",
            help="The skip rule for the task",
        )
        skip_rule.add_argument(
            "--clear-skip-rule",
            dest="clear_skip_rule",
            default=False,
            action="store_const",
            const=True,
            help="Clear the skip rule of the chore",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        ref_id = EntityId.from_raw(args.ref_id)
        if args.name:
            name = UpdateAction.change_to(ChoreName.from_raw(args.name))
        else:
            name = UpdateAction.do_nothing()
        if args.period:
            period = UpdateAction.change_to(RecurringTaskPeriod.from_raw(args.period))
        else:
            period = UpdateAction.do_nothing()
        eisen: UpdateAction[Optional[Eisen]]
        if args.clear_eisen:
            eisen = UpdateAction.change_to(None)
        elif args.eisen:
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
                    period.just_the_value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.actionable_from_day,
                ),
            )
        else:
            actionable_from_day = UpdateAction.do_nothing()
        actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_actionable_from_month:
            actionable_from_month = UpdateAction.change_to(None)
        elif args.actionable_from_month:
            actionable_from_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    period.just_the_value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.actionable_from_month,
                ),
            )
        else:
            actionable_from_month = UpdateAction.do_nothing()
        due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        if args.clear_due_at_time:
            due_at_time = UpdateAction.change_to(None)
        elif args.due_at_time:
            due_at_time = UpdateAction.change_to(
                RecurringTaskDueAtTime.from_raw(args.due_at_time),
            )
        else:
            due_at_time = UpdateAction.do_nothing()
        due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        if args.clear_due_at_day:
            due_at_day = UpdateAction.change_to(None)
        elif args.due_at_day:
            due_at_day = UpdateAction.change_to(
                RecurringTaskDueAtDay.from_raw(
                    period.just_the_value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.due_at_day,
                ),
            )
        else:
            due_at_day = UpdateAction.do_nothing()
        due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        if args.clear_due_at_month:
            due_at_month = UpdateAction.change_to(None)
        elif args.due_at_month:
            due_at_month = UpdateAction.change_to(
                RecurringTaskDueAtMonth.from_raw(
                    period.just_the_value
                    if period.should_change
                    else RecurringTaskPeriod.YEARLY,
                    args.due_at_month,
                ),
            )
        else:
            due_at_month = UpdateAction.do_nothing()
        if args.start_at_date:
            start_at_date = UpdateAction.change_to(
                ADate.from_raw(self._global_properties.timezone, args.start_at_date),
            )
        else:
            start_at_date = UpdateAction.do_nothing()
        end_at_date: UpdateAction[Optional[ADate]]
        if args.clear_end_at_date:
            end_at_date = UpdateAction.change_to(None)
        elif args.end_at_date:
            end_at_date = UpdateAction.change_to(
                ADate.from_raw(self._global_properties.timezone, args.end_at_date),
            )
        else:
            end_at_date = UpdateAction.do_nothing()
        if args.must_do:
            must_do = UpdateAction.change_to(True)
        elif args.can_skip:
            must_do = UpdateAction.change_to(False)
        else:
            must_do = UpdateAction.do_nothing()
        skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]]
        if args.clear_skip_rule:
            skip_rule = UpdateAction.change_to(None)
        elif args.skip_rule:
            skip_rule = UpdateAction.change_to(
                RecurringTaskSkipRule.from_raw(args.skip_rule),
            )
        else:
            skip_rule = UpdateAction.do_nothing()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ChoreUpdateArgs(
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
                must_do=must_do,
                skip_rule=skip_rule,
                start_at_date=start_at_date,
                end_at_date=end_at_date,
            ),
        )
