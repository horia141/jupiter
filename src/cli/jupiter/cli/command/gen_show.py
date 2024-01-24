"""ommand for loading previous runs of Gen."""


from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    boolean_to_rich_text,
    date_with_label_to_rich_text,
    entity_id_to_rich_text,
    entity_summary_snippet_to_rich_text,
    entity_tag_to_rich_text,
    event_source_to_rich_text,
    period_to_rich_text,
    sync_target_to_rich_text,
)
from jupiter.core.use_cases.gen.load_runs import GenLoadRunsResult, GenLoadRunsUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class GenShow(LoggedInReadonlyCommand[GenLoadRunsUseCase]):
    """Command for loading previous runs of task generation."""

    def _render_result(self, result: GenLoadRunsResult) -> None:
        rich_tree = Tree("🗑  Task Generation", guide_style="bold bright_blue")

        for entry in result.entries:
            entry_text = Text("Run from ")
            entry_text.append(event_source_to_rich_text(entry.source))
            entry_text.append(
                f" on {entry.created_time.as_date()} with {len(entry.entity_created_records)} entities created, "
            )
            entry_text.append(f"{len(entry.entity_updated_records)} entities updated, ")
            entry_text.append(
                f"and {len(entry.entity_removed_records)} entities removed"
            )

            entry_tree = rich_tree.add(entry_text)

            entry_tree.add(
                boolean_to_rich_text(
                    entry.gen_even_if_not_modified, "Generate even if not modified"
                )
            )

            entry_tree.add(date_with_label_to_rich_text(entry.today, "Generate for"))

            gen_targets_text = Text("Gen targets:")
            for gen_target in entry.gen_targets:
                gen_targets_text.append(" ")
                gen_targets_text.append(sync_target_to_rich_text(gen_target))
            entry_tree.add(gen_targets_text)

            period_text = Text("Period:")
            if entry.period is not None:
                for period in entry.period:
                    period_text.append(" ")
                    period_text.append(period_to_rich_text(period))
            else:
                period_text.append(" All")
            entry_tree.add(period_text)

            filter_project_ref_ids_text = Text("Filter project ref ids:")
            if entry.filter_project_ref_ids is not None:
                for ref_id in entry.filter_project_ref_ids:
                    filter_project_ref_ids_text.append(" ")
                    filter_project_ref_ids_text.append(entity_id_to_rich_text(ref_id))
            else:
                filter_project_ref_ids_text.append(" All")
            entry_tree.add(filter_project_ref_ids_text)

            filter_habit_ref_ids_text = Text("Filter habit ref ids:")
            if entry.filter_habit_ref_ids is not None:
                for ref_id in entry.filter_habit_ref_ids:
                    filter_habit_ref_ids_text.append(" ")
                    filter_habit_ref_ids_text.append(entity_id_to_rich_text(ref_id))
            else:
                filter_habit_ref_ids_text.append(" All")
            entry_tree.add(filter_habit_ref_ids_text)

            filter_chore_ref_ids_text = Text("Filter chore ref ids:")
            if entry.filter_chore_ref_ids is not None:
                for ref_id in entry.filter_chore_ref_ids:
                    filter_chore_ref_ids_text.append(" ")
                    filter_chore_ref_ids_text.append(entity_id_to_rich_text(ref_id))
            else:
                filter_chore_ref_ids_text.append(" All")
            entry_tree.add(filter_chore_ref_ids_text)

            filter_metric_ref_ids_text = Text("Filter metric ref ids:")
            if entry.filter_metric_ref_ids is not None:
                for ref_id in entry.filter_metric_ref_ids:
                    filter_metric_ref_ids_text.append(" ")
                    filter_metric_ref_ids_text.append(entity_id_to_rich_text(ref_id))
            else:
                filter_metric_ref_ids_text.append(" All")
            entry_tree.add(filter_metric_ref_ids_text)

            filter_person_ref_ids_text = Text("Filter person ref ids:")
            if entry.filter_person_ref_ids is not None:
                for ref_id in entry.filter_person_ref_ids:
                    filter_person_ref_ids_text.append(" ")
                    filter_person_ref_ids_text.append(entity_id_to_rich_text(ref_id))
            else:
                filter_person_ref_ids_text.append(" All")
            entry_tree.add(filter_person_ref_ids_text)

            filter_slack_task_ref_ids_text = Text("Filter Slack task ref ids:")
            if entry.filter_slack_task_ref_ids is not None:
                for ref_id in entry.filter_slack_task_ref_ids:
                    filter_slack_task_ref_ids_text.append(" ")
                    filter_slack_task_ref_ids_text.append(
                        entity_id_to_rich_text(ref_id)
                    )
            else:
                filter_slack_task_ref_ids_text.append(" All")
            entry_tree.add(filter_slack_task_ref_ids_text)

            filter_email_task_ref_ids_text = Text("Filter email task ref ids:")
            if entry.filter_email_task_ref_ids is not None:
                for ref_id in entry.filter_email_task_ref_ids:
                    filter_email_task_ref_ids_text.append(" ")
                    filter_email_task_ref_ids_text.append(
                        entity_id_to_rich_text(ref_id)
                    )
            else:
                filter_email_task_ref_ids_text.append(" All")
            entry_tree.add(filter_email_task_ref_ids_text)

            if len(entry.entity_created_records) > 0:
                created_entity_tree = entry_tree.add("Created entities:")

                for entity_record in entry.entity_created_records:
                    record_text = entity_tag_to_rich_text(entity_record.entity_tag)
                    record_text.append(entity_id_to_rich_text(entity_record.ref_id))
                    record_text.append(" ")
                    record_text.append(
                        entity_summary_snippet_to_rich_text(entity_record.snippet)
                    )
                    created_entity_tree.add(record_text)

            if len(entry.entity_updated_records) > 0:
                updated_entity_tree = entry_tree.add("Updated entities:")

                for entity_record in entry.entity_updated_records:
                    record_text = entity_tag_to_rich_text(entity_record.entity_tag)
                    record_text.append(entity_id_to_rich_text(entity_record.ref_id))
                    record_text.append(" ")
                    record_text.append(
                        entity_summary_snippet_to_rich_text(entity_record.snippet)
                    )
                    updated_entity_tree.add(record_text)

            if len(entry.entity_removed_records) > 0:
                removed_entity_tree = entry_tree.add("Removed entities:")

                for entity_record in entry.entity_removed_records:
                    record_text = entity_tag_to_rich_text(entity_record.entity_tag)
                    record_text.append(entity_id_to_rich_text(entity_record.ref_id))
                    record_text.append(" ")
                    record_text.append(
                        entity_summary_snippet_to_rich_text(entity_record.snippet)
                    )
                    removed_entity_tree.add(record_text)

        console = Console()
        console.print(rich_tree)
