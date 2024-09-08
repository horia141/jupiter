"""UseCase for showing the chores."""
from typing import cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    actionable_from_day_to_rich_text,
    actionable_from_month_to_rich_text,
    difficulty_to_rich_text,
    due_at_day_to_rich_text,
    due_at_month_to_rich_text,
    eisen_to_rich_text,
    end_date_to_rich_text,
    entity_id_to_rich_text,
    inbox_task_summary_to_rich_text,
    period_to_rich_text,
    project_to_rich_text,
    skip_rule_to_rich_text,
    start_date_to_rich_text,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.concept.chores.find import ChoreFindResult, ChoreFindUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class ChoreShow(LoggedInReadonlyCommand[ChoreFindUseCase, ChoreFindResult]):
    """UseCase class for showing the chores."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: ChoreFindResult,
    ) -> None:
        rich_tree = Tree("♻️  Chores", guide_style="bold bright_blue")

        sorted_chores = sorted(
            result.entries,
            key=lambda ce: (
                ce.chore.archived,
                ce.chore.suspended,
                ce.chore.gen_params.period,
                ce.chore.gen_params.eisen,
                ce.chore.gen_params.difficulty or Difficulty.EASY,
            ),
        )

        for chore_entry in sorted_chores:
            chore = chore_entry.chore
            project = cast(Project, chore_entry.project)
            inbox_tasks = chore_entry.inbox_tasks

            chore_text = Text("")
            chore_text.append(entity_id_to_rich_text(chore.ref_id))
            chore_text.append(f" {chore.name}")

            chore_info_text = Text("")
            chore_info_text.append(period_to_rich_text(chore.gen_params.period))
            chore_info_text.append(" ")
            chore_info_text.append(
                eisen_to_rich_text(chore.gen_params.eisen or Eisen.REGULAR)
            )

            if chore.gen_params.difficulty:
                chore_info_text.append(" ")
                chore_info_text.append(
                    difficulty_to_rich_text(chore.gen_params.difficulty),
                )

            if chore.skip_rule and str(chore.skip_rule) != "none":
                chore_info_text.append(" ")
                chore_info_text.append(skip_rule_to_rich_text(chore.skip_rule))

            if chore.gen_params.actionable_from_day:
                chore_info_text.append(" ")
                chore_info_text.append(
                    actionable_from_day_to_rich_text(
                        chore.gen_params.actionable_from_day,
                    ),
                )

            if chore.gen_params.actionable_from_month:
                chore_info_text.append(" ")
                chore_info_text.append(
                    actionable_from_month_to_rich_text(
                        chore.gen_params.actionable_from_month,
                    ),
                )

            if chore.gen_params.due_at_day:
                chore_info_text.append(" ")
                chore_info_text.append(
                    due_at_day_to_rich_text(chore.gen_params.due_at_day),
                )

            if chore.gen_params.due_at_month:
                chore_info_text.append(" ")
                chore_info_text.append(
                    due_at_month_to_rich_text(chore.gen_params.due_at_month),
                )

            if chore.start_at_date:
                chore_info_text.append(" ")
                chore_info_text.append(start_date_to_rich_text(chore.start_at_date))

            if chore.end_at_date:
                chore_info_text.append(" ")
                chore_info_text.append(end_date_to_rich_text(chore.end_at_date))

            if project is not None and context.workspace.is_feature_available(
                WorkspaceFeature.PROJECTS
            ):
                chore_info_text.append(" ")
                chore_info_text.append(project_to_rich_text(project.name))

            if chore.suspended:
                chore_text.stylize("yellow")
                chore_info_text.append(" #suspended")
                chore_info_text.stylize("yellow")

            if chore.archived:
                chore_text.stylize("gray62")
                chore_info_text.stylize("gray62")

            chore_tree = rich_tree.add(
                chore_text,
                guide_style="gray62" if chore.archived else "blue",
            )
            chore_tree.add(chore_info_text)

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
                chore_tree.add(inbox_task_text)

        console.print(rich_tree)
