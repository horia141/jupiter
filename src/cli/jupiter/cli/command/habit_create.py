"""UseCase for adding a habit."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.habits.create import HabitCreateArgs, HabitCreateUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession


class HabitCreate(LoggedInMutationCommand[HabitCreateUseCase]):
    """UseCase class for creating a habit."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            parser.add_argument(
                "--project-id",
                dest="project_ref_id",
                required=False,
                help="The project to add the task to",
            )
        parser.add_argument(
            "--name",
            dest="name",
            required=True,
            help="The name of the habit",
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
            "--skip-rule",
            dest="skip_rule",
            help="The skip rule for the task",
        )
        parser.add_argument(
            "--repeats-in-period",
            dest="repeats_in_period_count",
            type=int,
            help="How many times should the task repeat in the period",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            project_ref_id = (
                EntityId.from_raw(args.project_ref_id) if args.project_ref_id else None
            )
        else:
            project_ref_id = None
        name = HabitName.from_raw(args.name)
        period = RecurringTaskPeriod.from_raw(args.period)
        eisen = Eisen.from_raw(args.eisen) if args.eisen else None
        difficulty = Difficulty.from_raw(args.difficulty) if args.difficulty else None
        actionable_from_day = (
            RecurringTaskDueAtDay.from_raw_with_period(period, args.actionable_from_day)
            if args.actionable_from_day
            else None
        )
        actionable_from_month = (
            RecurringTaskDueAtMonth.from_raw_with_period(
                period, args.actionable_from_month
            )
            if args.actionable_from_month
            else None
        )
        due_at_time = (
            RecurringTaskDueAtTime.from_raw(args.due_at_time)
            if args.due_at_time
            else None
        )
        due_at_day = (
            RecurringTaskDueAtDay.from_raw_with_period(period, args.due_at_day)
            if args.due_at_day
            else None
        )
        due_at_month = (
            RecurringTaskDueAtMonth.from_raw_with_period(period, args.due_at_month)
            if args.due_at_month
            else None
        )
        skip_rule = (
            RecurringTaskSkipRule.from_raw(args.skip_rule) if args.skip_rule else None
        )
        repeats_in_period_count = args.repeats_in_period_count

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            HabitCreateArgs(
                project_ref_id=project_ref_id,
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
            ),
        )
