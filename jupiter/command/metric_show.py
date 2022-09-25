"""UseCase for showing metrics."""
from argparse import Namespace, ArgumentParser
from typing import Final, Optional

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    entity_key_to_rich_text,
    period_to_rich_text,
    eisen_to_rich_text,
    difficulty_to_rich_text,
    metric_unit_to_rich_text,
    due_at_time_to_rich_text,
    due_at_day_to_rich_text,
    due_at_month_to_rich_text,
    actionable_from_day_to_rich_text,
    actionable_from_month_to_rich_text,
    inbox_task_summary_to_rich_text,
    entity_id_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.domain.adate import ADate
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.use_cases.metrics.find import MetricFindUseCase
from jupiter.utils.global_properties import GlobalProperties


class MetricShow(command.ReadonlyCommand):
    """UseCase for showing metrics."""

    _global_properties: Final[GlobalProperties]
    _command: Final[MetricFindUseCase]

    def __init__(
        self, global_properties: GlobalProperties, the_command: MetricFindUseCase
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the metrics"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--show-archived",
            dest="show_archived",
            default=False,
            action="store_true",
            help="Whether to show archived vacations or not",
        )
        parser.add_argument(
            "--metric",
            dest="metric_keys",
            required=False,
            default=[],
            action="append",
            help="The key of the metric",
        )
        parser.add_argument(
            "--show-inbox-tasks",
            dest="show_inbox_tasks",
            default=False,
            action="store_const",
            const=True,
            help="Show inbox tasks",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        show_archived = args.show_archived
        metric_keys = (
            [MetricKey.from_raw(mk) for mk in args.metric_keys]
            if len(args.metric_keys) > 0
            else None
        )

        show_inbox_tasks = args.show_inbox_tasks

        result = self._command.execute(
            progress_reporter,
            MetricFindUseCase.Args(
                allow_archived=show_archived, filter_keys=metric_keys
            ),
        )

        sorted_metrics = sorted(
            result.metrics, key=lambda me: (me.metric.archived, me.metric.created_time)
        )

        rich_tree = Tree("📈 Metrics", guide_style="bold bright_blue")

        collection_project_text = Text(
            f"The collection project is {result.collection_project.name}"
        )
        rich_tree.add(collection_project_text)

        for metric_result_entry in sorted_metrics:
            metric = metric_result_entry.metric
            metric_entries = metric_result_entry.metric_entries
            collection_inbox_tasks = metric_result_entry.metric_collection_inbox_tasks

            metric_text = Text("")
            metric_text.append(entity_key_to_rich_text(metric.key))
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
                    period_to_rich_text(metric.collection_params.period)
                )
                metric_info_text.append(" ")
                metric_info_text.append(
                    eisen_to_rich_text(metric.collection_params.eisen)
                )

                if metric.collection_params.difficulty:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        difficulty_to_rich_text(metric.collection_params.difficulty)
                    )

                if metric.collection_params.actionable_from_day:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        actionable_from_day_to_rich_text(
                            metric.collection_params.actionable_from_day
                        )
                    )

                if metric.collection_params.actionable_from_month:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        actionable_from_month_to_rich_text(
                            metric.collection_params.actionable_from_month
                        )
                    )

                if metric.collection_params.due_at_time:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        due_at_time_to_rich_text(metric.collection_params.due_at_time)
                    )

                if metric.collection_params.due_at_day:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        due_at_day_to_rich_text(metric.collection_params.due_at_day)
                    )

                if metric.collection_params.due_at_month:
                    metric_info_text.append(" ")
                    metric_info_text.append(
                        due_at_month_to_rich_text(metric.collection_params.due_at_month)
                    )

            if metric.archived:
                metric_text.stylize("gray62")
                metric_info_text.stylize("gray62")

            metric_tree = rich_tree.add(
                metric_text, guide_style="gray62" if metric.archived else "blue"
            )
            metric_tree.add(metric_info_text)

            if len(metric_entries) > 0:
                sorted_metric_entries = sorted(
                    metric_entries, key=lambda me: (me.archived, me.collection_time)
                )

                previous_value: Optional[float] = None

                for metric_entry in sorted_metric_entries:
                    metric_entry_text = Text("")
                    metric_entry_text.append(
                        entity_id_to_rich_text(metric_entry.ref_id)
                    )
                    metric_entry_text.append(" ")
                    metric_entry_text.append(
                        ADate.to_user_date_str(metric_entry.collection_time)
                    )
                    metric_entry_text.append(" value=")
                    metric_entry_text.append(str(metric_entry.value))

                    if previous_value is not None:
                        if metric_entry.value > previous_value:
                            metric_entry_text.append(" ⬆️ ")
                        elif metric_entry.value < previous_value:
                            metric_entry_text.append(" ⬇️ ")

                    if metric_entry.notes:
                        metric_entry_text.append(" notes=")
                        metric_entry_text.append(metric_entry.notes, style="italic")

                    if metric_entry.archived:
                        metric_entry_text.stylize("gray62")

                    metric_tree.add(metric_entry_text)

                    previous_value = metric_entry.value

            if not show_inbox_tasks:
                continue
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

        console = Console()
        console.print(rich_tree)
