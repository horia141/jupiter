"""UseCase for generating reports of progress."""
from typing import List

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
    inbox_task_status_to_rich_text,
    period_to_rich_text,
    user_score_overview_to_rich,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.report.report_breakdown import ReportBreakdown
from jupiter.core.domain.report.report_period_result import (
    InboxTasksSummary,
    WorkableSummary,
)
from jupiter.core.use_cases.report import (
    ReportResult,
    ReportUseCase,
)
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class Report(LoggedInReadonlyCommand[ReportUseCase]):
    """UseCase class for reporting progress."""

    def _render_result(self, console: Console, result: ReportResult) -> None:
        sources_to_present = result.period_result.sources

        today_str = ADate.to_user_date_str(result.period_result.today)

        rich_text = Text("🚀 ")
        rich_text.append(period_to_rich_text(result.period_result.period))
        rich_text.append(f" as of {today_str}:")

        rich_tree = Tree(
            rich_text,
            guide_style="bold bright_blue",
        )

        if result.period_result.user_score_overview is not None:
            rich_tree.add(
                user_score_overview_to_rich(result.period_result.user_score_overview)
            )

        if ReportBreakdown.GLOBAL in result.period_result.breakdowns:
            global_text = Text("🌍 Global:")

            global_tree = rich_tree.add(global_text)

            inbox_task_table = self._build_inbox_tasks_summary_table(
                result.period_result.global_inbox_tasks_summary,
                sources_to_present,
            )
            global_tree.add(inbox_task_table)

            if self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.BIG_PLANS
            ):
                big_plan_tree = self._build_big_plans_summary_tree(
                    result.period_result.global_big_plans_summary,
                )
                global_tree.add(big_plan_tree)

        if (
            self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.PROJECTS
            )
            and ReportBreakdown.PROJECTS in result.period_result.breakdowns
        ):
            global_text = Text("💡 By Projects:")

            global_tree = rich_tree.add(global_text)

            for project_item in result.period_result.per_project_breakdown:
                project_text = entity_name_to_rich_text(project_item.name)

                project_tree = global_tree.add(project_text)

                inbox_task_table = self._build_inbox_tasks_summary_table(
                    project_item.inbox_tasks_summary,
                    sources_to_present,
                )
                project_tree.add(inbox_task_table)

                if self._top_level_context.workspace.is_feature_available(
                    WorkspaceFeature.BIG_PLANS
                ):
                    big_plan_tree = self._build_big_plans_summary_tree(
                        project_item.big_plans_summary,
                    )
                    global_tree.add(big_plan_tree)

        if ReportBreakdown.PERIODS in result.period_result.breakdowns:
            global_text = Text("⌛ By Periods:")

            global_tree = rich_tree.add(global_text)

            if not result.period_result.per_period_breakdown:
                raise Exception(
                    "Did not find any per period breakdown even if it's asked for",
                )

            for period_item in result.period_result.per_period_breakdown:
                period_text = entity_name_to_rich_text(period_item.name)

                period_tree = global_tree.add(period_text)

                inbox_task_table = self._build_inbox_tasks_summary_table(
                    period_item.inbox_tasks_summary,
                    sources_to_present,
                )
                period_tree.add(inbox_task_table)

                if self._top_level_context.workspace.is_feature_available(
                    WorkspaceFeature.BIG_PLANS
                ):
                    big_plan_tree = self._build_big_plans_summary_tree(
                        period_item.big_plans_summary,
                    )
                    global_tree.add(big_plan_tree)

        if (
            self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.HABITS
            )
            and ReportBreakdown.HABITS in result.period_result.breakdowns
        ):
            global_text = Text("💪 By Habits:")

            global_tree = rich_tree.add(global_text)

            for print_period in RecurringTaskPeriod:
                try:
                    max_breakdown_streak_size = max(
                        len(b.summary.streak_plot)
                        for b in result.period_result.per_habit_breakdown
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

                for habit_item in result.period_result.per_habit_breakdown:
                    if habit_item.archived:
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
            self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.CHORES
            )
            and ReportBreakdown.CHORES in result.period_result.breakdowns
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

                for chore_item in result.period_result.per_chore_breakdown:
                    if chore_item.archived:
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
            self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.BIG_PLANS
            )
            and ReportBreakdown.BIG_PLANS in result.period_result.breakdowns
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
                result.period_result.per_big_plan_breakdown,
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

        console.print(rich_tree)

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
