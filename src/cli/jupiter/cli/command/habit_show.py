"""UseCase for showing the habits."""
from typing import cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    actionable_from_day_to_rich_text,
    actionable_from_month_to_rich_text,
    difficulty_to_rich_text,
    due_at_day_to_rich_text,
    due_at_month_to_rich_text,
    eisen_to_rich_text,
    entity_id_to_rich_text,
    inbox_task_summary_to_rich_text,
    period_to_rich_text,
    project_to_rich_text,
    skip_rule_to_rich_text,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.concept.habits.find import HabitFindResult, HabitFindUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class HabitShow(LoggedInReadonlyCommand[HabitFindUseCase, HabitFindResult]):
    """UseCase class for showing the habits."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: HabitFindResult,
    ) -> None:
        rich_tree = Tree("💪️ Habits", guide_style="bold bright_blue")

        sorted_habits = sorted(
            result.entries,
            key=lambda ce: (
                ce.habit.archived,
                ce.habit.suspended,
                ce.habit.gen_params.period,
                ce.habit.gen_params.eisen,
                ce.habit.gen_params.difficulty or Difficulty.EASY,
            ),
        )

        for habit_entry in sorted_habits:
            habit = habit_entry.habit
            project = cast(Project, habit_entry.project)
            inbox_tasks = habit_entry.inbox_tasks

            habit_text = Text("")
            habit_text.append(entity_id_to_rich_text(habit.ref_id))
            habit_text.append(f" {habit.name}")

            habit_info_text = Text("")
            habit_info_text.append(period_to_rich_text(habit.gen_params.period))
            habit_info_text.append(" ")
            habit_info_text.append(
                eisen_to_rich_text(habit.gen_params.eisen or Eisen.REGULAR)
            )

            if habit.gen_params.difficulty:
                habit_info_text.append(" ")
                habit_info_text.append(
                    difficulty_to_rich_text(habit.gen_params.difficulty),
                )

            if habit.gen_params.skip_rule:
                habit_info_text.append(" ")
                habit_info_text.append(
                    skip_rule_to_rich_text(habit.gen_params.skip_rule)
                )

            if habit.gen_params.actionable_from_day:
                habit_info_text.append(" ")
                habit_info_text.append(
                    actionable_from_day_to_rich_text(
                        habit.gen_params.actionable_from_day,
                    ),
                )

            if habit.gen_params.actionable_from_month:
                habit_info_text.append(" ")
                habit_info_text.append(
                    actionable_from_month_to_rich_text(
                        habit.gen_params.actionable_from_month,
                    ),
                )

            if habit.gen_params.due_at_day:
                habit_info_text.append(" ")
                habit_info_text.append(
                    due_at_day_to_rich_text(habit.gen_params.due_at_day),
                )

            if habit.gen_params.due_at_month:
                habit_info_text.append(" ")
                habit_info_text.append(
                    due_at_month_to_rich_text(habit.gen_params.due_at_month),
                )

            if project is not None and context.workspace.is_feature_available(
                WorkspaceFeature.PROJECTS
            ):
                habit_info_text.append(" ")
                habit_info_text.append(project_to_rich_text(project.name))

            if habit.suspended:
                habit_text.stylize("yellow")
                habit_info_text.append(" #suspended")
                habit_info_text.stylize("yellow")

            if habit.archived:
                habit_text.stylize("gray62")
                habit_info_text.stylize("gray62")

            habit_tree = rich_tree.add(
                habit_text,
                guide_style="gray62" if habit.archived else "blue",
            )
            habit_tree.add(habit_info_text)

            if inbox_tasks is None or len(inbox_tasks) == 0:
                continue

            sorted_inbox_tasks = sorted(
                inbox_tasks,
                key=lambda it: (
                    it.archived,
                    it.status,
                    it.due_date if it.due_date else ADate.from_str("2100-01-01"),
                ),
            )

            for inbox_task in sorted_inbox_tasks:
                inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
                habit_tree.add(inbox_task_text)

        console.print(rich_tree)
