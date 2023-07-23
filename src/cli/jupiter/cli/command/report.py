"""UseCase for generating reports of progress."""
from argparse import ArgumentParser, Namespace
from typing import Final, List

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    inbox_task_status_to_rich_text,
    period_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.report import (
    InboxTasksSummary,
    ReportArgs,
    ReportUseCase,
    WorkableSummary,
)
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class Report(LoggedInReadonlyCommand[ReportUseCase]):
    """UseCase class for reporting progress."""

    _SOURCES_TO_REPORT = [
        InboxTaskSource.USER,
        InboxTaskSource.HABIT,
        InboxTaskSource.CHORE,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
    ]

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: ReportUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties
        self._time_provider = time_provider

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "report"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Report on progress"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--today",
            help="The date on which the upsert should run at",
        )
        parser.add_argument(
            "--source",
            dest="sources",
            default=[],
            action="append",
            choices=self._top_level_context.workspace.infer_sources_for_enabled_features(
                None
            ),
            help="Allow only inbox tasks form this particular source. Defaults to all",
        )
        if self._top_level_context.workspace.is_feature_available(Feature.PROJECTS):
            parser.add_argument(
                "--project-id",
                dest="project_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from this project",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.HABITS):
            parser.add_argument(
                "--habit-id",
                dest="habit_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from these habits",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.CHORES):
            parser.add_argument(
                "--chore-id",
                dest="chore_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from these chores",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS):
            parser.add_argument(
                "--big-plan-id",
                dest="big_plan_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from these big plans",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.METRICS):
            parser.add_argument(
                "--metric-id",
                dest="metric_ref_ids",
                required=False,
                default=[],
                action="append",
                help="Allow only tasks from this metric",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.PERSONS):
            parser.add_argument(
                "--person-id",
                dest="person_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from these persons",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.SLACK_TASKS):
            parser.add_argument(
                "--slack-task-id",
                dest="slack_task_ref_ids",
                default=[],
                action="append",
                help="Allow only these Slack tasks",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.EMAIL_TASKS):
            parser.add_argument(
                "--email-task-id",
                dest="email_task_ref_ids",
                default=[],
                action="append",
                help="Allow only these email tasks",
            )
        if self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS):
            parser.add_argument(
                "--cover",
                dest="covers",
                default=["inbox-tasks", "big-plans"],
                choices=["inbox-tasks", "big-plans"],
                help="Show reporting info about certain parts",
            )
        allowed_breakdowns = ["global", "periods"]
        if self._top_level_context.workspace.is_feature_available(Feature.PROJECTS):
            allowed_breakdowns.append("projects")
        if self._top_level_context.workspace.is_feature_available(Feature.HABITS):
            allowed_breakdowns.append("habits")
        if self._top_level_context.workspace.is_feature_available(Feature.CHORES):
            allowed_breakdowns.append("chores")
        if self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS):
            allowed_breakdowns.append("big-plans")
        parser.add_argument(
            "--breakdown",
            dest="breakdowns",
            default=[],
            action="append",
            choices=[
                "global",
                "periods",
                "projects",
                "habits",
                "chores",
                "big-plans",
            ],
            help="Breakdown report by one or more dimensions",
        )
        parser.add_argument(
            "--sub-period",
            dest="breakdown_period",
            default=None,
            choices=RecurringTaskPeriod.all_values(),
            help="Specify subperiod to use when breaking down by period",
        )
        parser.add_argument(
            "--period",
            default=RecurringTaskPeriod.WEEKLY.value,
            dest="period",
            choices=RecurringTaskPeriod.all_values(),
            help="The period to report on",
        )
        parser.add_argument(
            "--show-archived",
            default=False,
            dest="show_archived",
            action="store_const",
            const=True,
            help="Whether to show archived entities",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        today = (
            ADate.from_raw(self._global_properties.timezone, args.today)
            if args.today
            else self._time_provider.get_current_date()
        )
        sources = (
            [InboxTaskSource.from_raw(s) for s in args.sources]
            if len(args.sources) > 0
            else None
        )
        if self._top_level_context.workspace.is_feature_available(Feature.PROJECTS):
            project_ref_ids = (
                [EntityId.from_raw(pk) for pk in args.project_ref_ids]
                if len(args.project_ref_ids) > 0
                else None
            )
        else:
            project_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.HABITS):
            habit_ref_ids = (
                [EntityId.from_raw(rt) for rt in args.habit_ref_ids]
                if len(args.habit_ref_ids) > 0
                else None
            )
        else:
            habit_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.CHORES):
            chore_ref_ids = (
                [EntityId.from_raw(rt) for rt in args.chore_ref_ids]
                if len(args.chore_ref_ids) > 0
                else None
            )
        else:
            chore_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS):
            big_plan_ref_ids = (
                [EntityId.from_raw(bp) for bp in args.big_plan_ref_ids]
                if len(args.big_plan_ref_ids) > 0
                else None
            )
        else:
            big_plan_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.METRICS):
            metric_ref_ids = (
                [EntityId.from_raw(mk) for mk in args.metric_ref_ids]
                if len(args.metric_ref_ids) > 0
                else None
            )
        else:
            metric_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.PERSONS):
            person_ref_ids = (
                [EntityId.from_raw(bp) for bp in args.person_ref_ids]
                if len(args.person_ref_ids) > 0
                else None
            )
        else:
            person_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.SLACK_TASKS):
            slack_task_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.slack_task_ref_ids]
                if len(args.slack_task_ref_ids) > 0
                else None
            )
        else:
            slack_task_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.EMAIL_TASKS):
            email_task_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.email_task_ref_ids]
                if len(args.email_task_ref_ids) > 0
                else None
            )
        else:
            email_task_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS):
            covers = args.covers
        else:
            covers = ["inbox-tasks"]
        breakdowns = (
            args.breakdowns if len(args.breakdowns) > 0 else ["global", "habits"]
        )
        breakdown_period_raw = (
            RecurringTaskPeriod.from_raw(args.breakdown_period)
            if args.breakdown_period
            else None
        )
        period = RecurringTaskPeriod.from_raw(args.period)
        show_archived = args.show_archived

        breakdown_period = None
        if "periods" in breakdowns:
            if breakdown_period_raw is None:
                breakdown_period = self._one_smaller_than_period(period)
            else:
                breakdown_period = breakdown_period_raw

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ReportArgs(
                today=today,
                filter_project_ref_ids=project_ref_ids,
                filter_sources=sources,
                filter_big_plan_ref_ids=big_plan_ref_ids,
                filter_habit_ref_ids=habit_ref_ids,
                filter_chore_ref_ids=chore_ref_ids,
                filter_metric_ref_ids=metric_ref_ids,
                filter_person_ref_ids=person_ref_ids,
                filter_slack_task_ref_ids=slack_task_ref_ids,
                filter_email_task_ref_ids=email_task_ref_ids,
                period=period,
                breakdown_period=breakdown_period,
            ),
        )

        sources_to_present = (
            self._top_level_context.workspace.infer_sources_for_enabled_features(
                (
                    [s for s in Report._SOURCES_TO_REPORT if s in sources]
                    if sources
                    else Report._SOURCES_TO_REPORT
                )
            )
        )

        today_str = ADate.to_user_date_str(today)

        rich_text = Text("🚀 ")
        rich_text.append(period_to_rich_text(period))
        rich_text.append(f" as of {today_str}:")

        rich_tree = Tree(
            rich_text,
            guide_style="bold bright_blue",
        )

        if "global" in breakdowns:
            global_text = Text("🌍 Global:")

            global_tree = rich_tree.add(global_text)

            if "inbox-tasks" in covers:
                inbox_task_table = self._build_inbox_tasks_summary_table(
                    result.global_inbox_tasks_summary,
                    sources_to_present,
                )
                global_tree.add(inbox_task_table)

            if (
                self._top_level_context.workspace.is_feature_available(
                    Feature.BIG_PLANS
                )
                and "big-plans" in covers
            ):
                big_plan_tree = self._build_big_plans_summary_tree(
                    result.global_big_plans_summary,
                )
                global_tree.add(big_plan_tree)

        if (
            self._top_level_context.workspace.is_feature_available(Feature.PROJECTS)
            and "projects" in breakdowns
        ):
            global_text = Text("💡 By Projects:")

            global_tree = rich_tree.add(global_text)

            for project_item in result.per_project_breakdown:
                project_text = entity_name_to_rich_text(project_item.name)

                project_tree = global_tree.add(project_text)

                if "inbox-tasks" in covers:
                    inbox_task_table = self._build_inbox_tasks_summary_table(
                        project_item.inbox_tasks_summary,
                        sources_to_present,
                    )
                    project_tree.add(inbox_task_table)

                if (
                    self._top_level_context.workspace.is_feature_available(
                        Feature.BIG_PLANS
                    )
                    and "big-plans" in covers
                ):
                    big_plan_tree = self._build_big_plans_summary_tree(
                        project_item.big_plans_summary,
                    )
                    global_tree.add(big_plan_tree)

        if "periods" in breakdowns:
            global_text = Text("⌛ By Periods:")

            global_tree = rich_tree.add(global_text)

            if not result.per_period_breakdown:
                raise Exception(
                    "Did not find any per period breakdown even if it's asked for",
                )

            for period_item in result.per_period_breakdown:
                period_text = entity_name_to_rich_text(period_item.name)

                period_tree = global_tree.add(period_text)

                if "inbox-tasks" in covers:
                    inbox_task_table = self._build_inbox_tasks_summary_table(
                        period_item.inbox_tasks_summary,
                        sources_to_present,
                    )
                    period_tree.add(inbox_task_table)

                if "big-plans" in covers:
                    big_plan_tree = self._build_big_plans_summary_tree(
                        period_item.big_plans_summary,
                    )
                    global_tree.add(big_plan_tree)

        if (
            self._top_level_context.workspace.is_feature_available(Feature.HABITS)
            and "habits" in breakdowns
        ):
            global_text = Text("💪 By Habits:")

            global_tree = rich_tree.add(global_text)

            for print_period in RecurringTaskPeriod:
                try:
                    max_breakdown_streak_size = max(
                        len(b.summary.streak_plot)
                        for b in result.per_habit_breakdown
                        if b.period == print_period
                    )
                except ValueError:
                    max_breakdown_streak_size = 1

                period_text = Text("").append(period_to_rich_text(print_period))
                period_table = Table(
                    title=period_text,
                    title_justify="left",
                    title_style="",
                )

                period_table.add_column("Id")
                period_table.add_column("Name", width=64, no_wrap=True)
                period_table.add_column("Streak")
                habit_created_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.NOT_STARTED,
                ).append(Text(" Created"))
                period_table.add_column(habit_created_text, width=12, justify="right")

                habit_accepted_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.ACCEPTED,
                ).append(Text(" Accepted"))
                period_table.add_column(habit_accepted_text, width=12, justify="right")

                habit_working_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.IN_PROGRESS,
                ).append(Text(" Working"))
                period_table.add_column(habit_working_text, width=12, justify="right")

                habit_not_done_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.NOT_DONE,
                ).append(Text(" Not Done"))
                period_table.add_column(habit_not_done_text, width=12, justify="right")

                habit_done_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.DONE,
                ).append(Text(" Done"))
                period_table.add_column(habit_done_text, width=12, justify="right")

                for habit_item in result.per_habit_breakdown:
                    if not show_archived and habit_item.archived:
                        continue
                    if habit_item.period != print_period:
                        continue

                    habit_id_text = Text("").append(
                        entity_id_to_rich_text(habit_item.ref_id),
                    )
                    habit_name_text = Text("").append(
                        entity_name_to_rich_text(habit_item.name),
                    )
                    habit_streak_text = Text(
                        f"{habit_item.summary.streak_plot.rjust(max_breakdown_streak_size, '_')}",
                    )

                    created_cnt_text = Text(f"{habit_item.summary.created_cnt}")
                    if habit_item.summary.created_cnt == 0:
                        created_cnt_text.stylize("dim")
                    accepted_cnt_text = Text(f"{habit_item.summary.accepted_cnt}")
                    if habit_item.summary.accepted_cnt == 0:
                        accepted_cnt_text.stylize("dim")
                    working_cnt_text = Text(f"{habit_item.summary.working_cnt}")
                    if habit_item.summary.working_cnt == 0:
                        working_cnt_text.stylize("dim")
                    not_done_cnt_text = Text(
                        f"{habit_item.summary.not_done_cnt} ({habit_item.summary.not_done_ratio * 100:.0f}%)",
                    )
                    if habit_item.summary.not_done_cnt == 0:
                        not_done_cnt_text.stylize("dim")
                    done_cnt_text = Text(
                        f"{habit_item.summary.done_cnt} ({habit_item.summary.done_ratio * 100:.0f}%)",
                    )
                    if habit_item.summary.done_cnt == 0:
                        done_cnt_text.stylize("dim")

                    period_table.add_row(
                        habit_id_text,
                        habit_name_text,
                        habit_streak_text,
                        created_cnt_text,
                        accepted_cnt_text,
                        working_cnt_text,
                        not_done_cnt_text,
                        done_cnt_text,
                    )

                global_tree.add(period_table)

        if (
            self._top_level_context.workspace.is_feature_available(Feature.CHORES)
            and "chores" in breakdowns
        ):
            global_text = Text("♻️ By Chores:")

            global_tree = rich_tree.add(global_text)

            for print_period in RecurringTaskPeriod:
                period_text = Text("").append(period_to_rich_text(print_period))
                period_table = Table(
                    title=period_text,
                    title_justify="left",
                    title_style="",
                )

                period_table.add_column("Id")
                period_table.add_column("Name", width=64, no_wrap=True)
                chore_created_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.NOT_STARTED,
                ).append(Text(" Created"))
                period_table.add_column(chore_created_text, width=12, justify="right")

                chore_accepted_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.ACCEPTED,
                ).append(Text(" Accepted"))
                period_table.add_column(chore_accepted_text, width=12, justify="right")

                chore_working_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.IN_PROGRESS,
                ).append(Text(" Working"))
                period_table.add_column(chore_working_text, width=12, justify="right")

                chore_not_done_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.NOT_DONE,
                ).append(Text(" Not Done"))
                period_table.add_column(chore_not_done_text, width=12, justify="right")

                chore_done_text = inbox_task_status_to_rich_text(
                    InboxTaskStatus.DONE,
                ).append(Text(" Done"))
                period_table.add_column(chore_done_text, width=12, justify="right")

                for chore_item in result.per_chore_breakdown:
                    if not show_archived and chore_item.archived:
                        continue
                    if chore_item.period != print_period:
                        continue

                    chore_id_text = Text("").append(
                        entity_id_to_rich_text(chore_item.ref_id),
                    )
                    chore_name_text = Text("").append(
                        entity_name_to_rich_text(chore_item.name),
                    )

                    created_cnt_text = Text(f"{chore_item.summary.created_cnt}")
                    if chore_item.summary.created_cnt == 0:
                        created_cnt_text.stylize("dim")
                    accepted_cnt_text = Text(f"{chore_item.summary.accepted_cnt}")
                    if chore_item.summary.accepted_cnt == 0:
                        accepted_cnt_text.stylize("dim")
                    working_cnt_text = Text(f"{chore_item.summary.working_cnt}")
                    if chore_item.summary.working_cnt == 0:
                        working_cnt_text.stylize("dim")
                    not_done_cnt_text = Text(
                        f"{chore_item.summary.not_done_cnt} ({chore_item.summary.not_done_ratio * 100:.0f}%)",
                    )
                    if chore_item.summary.not_done_cnt == 0:
                        not_done_cnt_text.stylize("dim")
                    done_cnt_text = Text(
                        f"{chore_item.summary.done_cnt} ({chore_item.summary.done_ratio * 100:.0f}%)",
                    )
                    if chore_item.summary.done_cnt == 0:
                        done_cnt_text.stylize("dim")

                    period_table.add_row(
                        chore_id_text,
                        chore_name_text,
                        created_cnt_text,
                        accepted_cnt_text,
                        working_cnt_text,
                        not_done_cnt_text,
                        done_cnt_text,
                    )

                global_tree.add(period_table)

        if (
            self._top_level_context.workspace.is_feature_available(Feature.BIG_PLANS)
            and "big-plans" in breakdowns
        ):
            global_table = Table(
                title="🌍 By Big Plan:",
                title_justify="left",
                title_style="",
            )

            global_table.add_column("Id")
            global_table.add_column("Name", width=64, no_wrap=True)
            big_plan_created_text = inbox_task_status_to_rich_text(
                InboxTaskStatus.NOT_STARTED,
            ).append(Text(" Created"))
            global_table.add_column(big_plan_created_text, width=12, justify="right")

            big_plan_accepted_text = inbox_task_status_to_rich_text(
                InboxTaskStatus.ACCEPTED,
            ).append(Text(" Accepted"))
            global_table.add_column(big_plan_accepted_text, width=12, justify="right")

            big_plan_working_text = inbox_task_status_to_rich_text(
                InboxTaskStatus.IN_PROGRESS,
            ).append(Text(" Working"))
            global_table.add_column(big_plan_working_text, width=12, justify="right")

            big_plan_not_done_text = inbox_task_status_to_rich_text(
                InboxTaskStatus.NOT_DONE,
            ).append(Text(" Not Done"))
            global_table.add_column(big_plan_not_done_text, width=12, justify="right")

            big_plan_done_text = inbox_task_status_to_rich_text(
                InboxTaskStatus.DONE,
            ).append(Text(" Done"))
            global_table.add_column(big_plan_done_text, width=12, justify="right")

            sorted_big_plans = sorted(
                result.per_big_plan_breakdown,
                key=lambda bpe: (
                    bpe.actionable_date
                    if bpe.actionable_date
                    else ADate.from_str("2100-01-01"),
                ),
            )

            for big_plan_item in sorted_big_plans:
                big_plan_id_text = Text("").append(
                    entity_id_to_rich_text(big_plan_item.ref_id),
                )
                big_plan_name_text = Text("").append(
                    entity_name_to_rich_text(big_plan_item.name),
                )

                created_cnt_text = Text(f"{big_plan_item.summary.created_cnt}")
                if big_plan_item.summary.created_cnt == 0:
                    created_cnt_text.stylize("dim")
                accepted_cnt_text = Text(f"{big_plan_item.summary.accepted_cnt}")
                if big_plan_item.summary.accepted_cnt == 0:
                    accepted_cnt_text.stylize("dim")
                working_cnt_text = Text(f"{big_plan_item.summary.working_cnt}")
                if big_plan_item.summary.working_cnt == 0:
                    working_cnt_text.stylize("dim")
                not_done_cnt_text = Text(
                    f"{big_plan_item.summary.not_done_cnt} ({big_plan_item.summary.not_done_ratio * 100:.0f}%)",
                )
                if big_plan_item.summary.not_done_cnt == 0:
                    not_done_cnt_text.stylize("dim")
                done_cnt_text = Text(
                    f"{big_plan_item.summary.done_cnt} ({big_plan_item.summary.done_ratio * 100:.0f}%)",
                )
                if big_plan_item.summary.done_cnt == 0:
                    done_cnt_text.stylize("dim")

                global_table.add_row(
                    big_plan_id_text,
                    big_plan_name_text,
                    created_cnt_text,
                    accepted_cnt_text,
                    working_cnt_text,
                    not_done_cnt_text,
                    done_cnt_text,
                )

            rich_tree.add(global_table)

        console = Console()
        console.print(rich_tree)

    @staticmethod
    def _one_smaller_than_period(period: RecurringTaskPeriod) -> RecurringTaskPeriod:
        if period == RecurringTaskPeriod.YEARLY:
            return RecurringTaskPeriod.QUARTERLY
        elif period == RecurringTaskPeriod.QUARTERLY:
            return RecurringTaskPeriod.MONTHLY
        elif period == RecurringTaskPeriod.MONTHLY:
            return RecurringTaskPeriod.WEEKLY
        elif period == RecurringTaskPeriod.WEEKLY:
            return RecurringTaskPeriod.DAILY
        else:
            raise InputValidationError("Cannot breakdown daily by period")

    @staticmethod
    def _build_inbox_tasks_summary_table(
        summary: InboxTasksSummary,
        sources_to_present: List[InboxTaskSource],
    ) -> Table:
        inbox_tasks_table = Table(
            title="📥 Inbox Tasks:",
            title_justify="left",
            title_style="",
        )

        inbox_tasks_table.add_column("State", width=16)
        inbox_tasks_table.add_column("Total", width=8, justify="right")
        for source in sources_to_present:
            inbox_tasks_table.add_column(source.to_nice(), width=10, justify="right")

        created_renderables = [
            Text("📥 Created"),
            Text(f"{summary.created.total_cnt}"),
        ]
        for source in sources_to_present:
            created_renderables.append(
                Text(
                    f"{next((i.count for i in summary.created.per_source_cnt if i.source == source), 0)}",
                ),
            )
        inbox_tasks_table.add_row(*created_renderables)

        accepted_renderables = [
            inbox_task_status_to_rich_text(InboxTaskStatus.ACCEPTED).append(
                Text(" Accepted"),
            ),
            Text(f"{summary.accepted.total_cnt}"),
        ]
        for source in sources_to_present:
            accepted_renderables.append(
                Text(
                    f"{next((i.count for i in summary.accepted.per_source_cnt if i.source == source), 0)}",
                ),
            )
        inbox_tasks_table.add_row(*accepted_renderables)

        working_renderables = [
            inbox_task_status_to_rich_text(InboxTaskStatus.IN_PROGRESS).append(
                Text(" Working"),
            ),
            Text(f"{summary.working.total_cnt}"),
        ]
        for source in sources_to_present:
            working_renderables.append(
                Text(
                    f"{next((i.count for i in summary.working.per_source_cnt if i.source == source), 0)}",
                ),
            )
        inbox_tasks_table.add_row(*working_renderables)

        not_done_renderables = [
            inbox_task_status_to_rich_text(InboxTaskStatus.NOT_DONE).append(
                Text(" Not Done"),
            ),
            Text(f"{summary.not_done.total_cnt}"),
        ]
        for source in sources_to_present:
            not_done_renderables.append(
                Text(
                    f"{next((i.count for i in summary.not_done.per_source_cnt if i.source == source), 0)}",
                ),
            )
        inbox_tasks_table.add_row(*not_done_renderables)

        done_renderables = [
            inbox_task_status_to_rich_text(InboxTaskStatus.DONE).append(Text(" Done")),
            Text(f"{summary.done.total_cnt}"),
        ]
        for source in sources_to_present:
            done_renderables.append(
                Text(
                    f"{next((i.count for i in summary.done.per_source_cnt if i.source == source), 0)}",
                ),
            )
        inbox_tasks_table.add_row(*done_renderables)

        return inbox_tasks_table

    @staticmethod
    def _build_big_plans_summary_tree(summary: WorkableSummary) -> Tree:
        big_plan_text = Text("🌍 Big Plans:")
        big_plan_tree = Tree(big_plan_text)

        created_text = inbox_task_status_to_rich_text(
            InboxTaskStatus.NOT_STARTED,
        ).append(Text(f" Created: {summary.created_cnt}"))
        big_plan_tree.add(created_text)

        accepted_text = inbox_task_status_to_rich_text(InboxTaskStatus.ACCEPTED).append(
            Text(f" Accepted: {summary.accepted_cnt}"),
        )
        big_plan_tree.add(accepted_text)

        working_text = inbox_task_status_to_rich_text(
            InboxTaskStatus.IN_PROGRESS,
        ).append(Text(f" Working: {summary.working_cnt}"))
        big_plan_tree.add(working_text)

        not_done_text = inbox_task_status_to_rich_text(InboxTaskStatus.NOT_DONE).append(
            Text(f" Not Done: {summary.not_done_cnt}"),
        )
        not_done_tree = big_plan_tree.add(not_done_text)

        sorted_not_done_big_plans = sorted(
            summary.not_done_big_plans,
            key=lambda bp: bp.actionable_date
            if bp.actionable_date
            else ADate.from_str("2100-01-01"),
        )

        for big_plan in sorted_not_done_big_plans:
            not_done_big_plan_text = Text("")
            not_done_big_plan_text.append(entity_id_to_rich_text(big_plan.ref_id))
            not_done_big_plan_text.append(" ")
            not_done_big_plan_text.append(entity_name_to_rich_text(big_plan.name))
            not_done_tree.add(not_done_big_plan_text)
        done_text = inbox_task_status_to_rich_text(InboxTaskStatus.DONE).append(
            Text(f" Done: {summary.done_cnt}"),
        )

        sorted_done_big_plans = sorted(
            summary.done_big_plans,
            key=lambda bp: bp.actionable_date
            if bp.actionable_date
            else ADate.from_str("2100-01-01"),
        )

        done_tree = big_plan_tree.add(done_text)
        for big_plan in sorted_done_big_plans:
            done_big_plan_text = Text("")
            done_big_plan_text.append(entity_id_to_rich_text(big_plan.ref_id))
            done_big_plan_text.append(" ")
            done_big_plan_text.append(entity_name_to_rich_text(big_plan.name))
            done_tree.add(done_big_plan_text)

        return big_plan_tree
