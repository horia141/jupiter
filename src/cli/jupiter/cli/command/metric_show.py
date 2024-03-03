"""UseCase for showing metrics."""
from typing import Optional, cast

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
    metric_unit_to_rich_text,
    period_to_rich_text,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note_content_block import ParagraphBlock
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from jupiter.core.use_cases.metrics.find import MetricFindResult, MetricFindUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class MetricShow(LoggedInReadonlyCommand[MetricFindUseCase, MetricFindResult]):
    """UseCase for showing metrics."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: MetricFindResult,
    ) -> None:
        sorted_metrics = sorted(
            result.entries,
            key=lambda me: (me.metric.archived, me.metric.created_time),
        )

        rich_tree = Tree("📈 Metrics", guide_style="bold bright_blue")

        if context.workspace.is_feature_available(WorkspaceFeature.PROJECTS):
            collection_project_text = Text(
                f"The collection project is {result.collection_project.name}",
            )
            rich_tree.add(collection_project_text)

        for metric_result_entry in sorted_metrics:
            metric = metric_result_entry.metric
            metric_entries = metric_result_entry.metric_entries
            collection_inbox_tasks = metric_result_entry.metric_collection_inbox_tasks
            notes_by_metric_entry_ref_id = (
                {
                    n.source_entity_ref_id: n
                    for n in metric_result_entry.metric_entry_notes
                }
                if metric_result_entry.metric_entry_notes
                else {}
            )

            metric_text = Text("")
            metric_text.append(entity_id_to_rich_text(metric.ref_id))
            if metric.icon:
                metric_text.append(" ")
                metric_text.append(str(metric.icon))
                metric_text.append(" ")
            metric_text.append(" ")
            metric_text.append(str(metric.name))

            if metric.metric_unit:
                metric_text.append(" (")
                metric_text.append(metric_unit_to_rich_text(metric.metric_unit))
                metric_text.append(")")

            metric_info_text = Text("")

            if metric.collection_params:
                metric_info_text.append(
                    period_to_rich_text(metric.collection_params.period),
                )
                if metric.collection_params.eisen:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        eisen_to_rich_text(metric.collection_params.eisen),
                    )

                if metric.collection_params.difficulty:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        difficulty_to_rich_text(metric.collection_params.difficulty),
                    )

                if metric.collection_params.actionable_from_day:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        actionable_from_day_to_rich_text(
                            metric.collection_params.actionable_from_day,
                        ),
                    )

                if metric.collection_params.actionable_from_month:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        actionable_from_month_to_rich_text(
                            metric.collection_params.actionable_from_month,
                        ),
                    )

                if metric.collection_params.due_at_day:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        due_at_day_to_rich_text(metric.collection_params.due_at_day),
                    )

                if metric.collection_params.due_at_month:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        due_at_month_to_rich_text(
                            metric.collection_params.due_at_month,
                        ),
                    )

            if metric.archived:
                metric_text.stylize("gray62")
                metric_info_text.stylize("gray62")

            metric_tree = rich_tree.add(
                metric_text,
                guide_style="gray62" if metric.archived else "blue",
            )
            metric_tree.add(metric_info_text)

            if metric_entries is not None and len(metric_entries) > 0:
                sorted_metric_entries = sorted(
                    metric_entries,
                    key=lambda me: (me.archived, me.collection_time),
                )

                previous_value: Optional[float] = None

                for metric_entry in sorted_metric_entries:
                    metric_entry_text = Text("")
                    metric_entry_text.append(
                        entity_id_to_rich_text(metric_entry.ref_id),
                    )
                    metric_entry_text.append(" ")
                    metric_entry_text.append(
                        str(metric_entry.collection_time),
                    )
                    metric_entry_text.append(" value=")
                    metric_entry_text.append(str(metric_entry.value))

                    if previous_value is not None:
                        if metric_entry.value > previous_value:
                            metric_entry_text.append(" ⬆️ ")
                        elif metric_entry.value < previous_value:
                            metric_entry_text.append(" ⬇️ ")

                    if metric_entry.ref_id in notes_by_metric_entry_ref_id:
                        note = notes_by_metric_entry_ref_id[metric_entry.ref_id]
                        note_paragraph = cast(ParagraphBlock, note.content[0]).text
                        metric_entry_text.append(" notes=")
                        metric_entry_text.append(note_paragraph, style="italic")

                    if metric_entry.archived:
                        metric_entry_text.stylize("gray62")

                    metric_tree.add(metric_entry_text)

                    previous_value = metric_entry.value

            if collection_inbox_tasks is None or len(collection_inbox_tasks) == 0:
                continue

            collection_inbox_task_tree = metric_tree.add("📥 Collection Tasks:")

            sorted_collection_inbox_tasks = sorted(
                collection_inbox_tasks,
                key=lambda it: (
                    it.archived,
                    it.status,
                    it.due_date if it.due_date else ADate.from_str("2100-01-01"),
                ),
            )

            for inbox_task in sorted_collection_inbox_tasks:
                inbox_task_text = inbox_task_summary_to_rich_text(inbox_task)
                collection_inbox_task_tree.add(inbox_task_text)

        console.print(rich_tree)
