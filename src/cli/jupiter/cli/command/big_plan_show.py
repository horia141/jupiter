"""UseCase for showing the big plans."""
from argparse import ArgumentParser, Namespace
from typing import cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    actionable_date_to_rich_text,
    big_plan_status_to_rich_text,
    due_date_to_rich_text,
    entity_id_to_rich_text,
    inbox_task_summary_to_rich_text,
    project_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.find import BigPlanFindArgs, BigPlanFindResult, BigPlanFindUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class BigPlanShow(LoggedInReadonlyCommand[BigPlanFindUseCase]):
    """UseCase class for showing the big plans."""

    def _render_result(self, result: BigPlanFindResult) -> None:
        sorted_big_plans = sorted(
            result.entries,
            key=lambda bpe: (
                bpe.big_plan.archived,
                bpe.big_plan.status,
                bpe.big_plan.actionable_date
                if bpe.big_plan.actionable_date
                else ADate.from_str("2100-01-01"),
            ),
        )

        rich_tree = Tree("🌍 Big Plans", guide_style="bold bright_blue")

        for big_plan_entry in sorted_big_plans:
            big_plan = big_plan_entry.big_plan
            project = cast(Project, big_plan_entry.project)
            inbox_tasks = big_plan_entry.inbox_tasks

            big_plan_text = big_plan_status_to_rich_text(
                big_plan.status,
                big_plan.archived,
            )
            big_plan_text.append(" ")
            big_plan_text.append(entity_id_to_rich_text(big_plan.ref_id))
            big_plan_text.append(f" {big_plan.name}")

            big_plan_info_text = Text("")
            if big_plan.actionable_date is not None:
                big_plan_info_text.append(
                    actionable_date_to_rich_text(big_plan.actionable_date),
                )

            if big_plan.due_date is not None:
                big_plan_info_text.append(" ")
                big_plan_info_text.append(due_date_to_rich_text(big_plan.due_date))

            if project is not None and self._top_level_context.workspace.is_feature_available(
                WorkspaceFeature.PROJECTS
            ):
                big_plan_info_text.append(" ")
                big_plan_info_text.append(project_to_rich_text(project.name))

            if big_plan.archived:
                big_plan_text.stylize("gray62")
                big_plan_info_text.stylize("gray62")

            big_plan_tree = rich_tree.add(
                big_plan_text,
                guide_style="gray62" if big_plan.archived else "blue",
            )
            big_plan_tree.add(big_plan_info_text)

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
                big_plan_tree.add(inbox_task_text)

        console = Console()
        console.print(rich_tree)
