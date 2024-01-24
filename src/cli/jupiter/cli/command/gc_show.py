"""ommand for loading previous runs of GC."""

from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_summary_snippet_to_rich_text,
    entity_tag_to_rich_text,
    event_source_to_rich_text,
    sync_target_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.use_cases.gc.load_runs import GCLoadRunsArgs, GCLoadRunsUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class GCShow(LoggedInReadonlyCommand[GCLoadRunsUseCase]):
    """Command for loading previous runs of GC."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            GCLoadRunsArgs(),
        )

        rich_tree = Tree("🗑  GC", guide_style="bold bright_blue")

        for entry in result.entries:
            entry_text = Text("Run from ")
            entry_text.append(event_source_to_rich_text(entry.source))
            entry_text.append(
                f" on {entry.created_time.as_date()} with {len(entry.entity_records)} entities archived"
            )

            entry_tree = rich_tree.add(entry_text)

            gc_targets_text = Text("GC targets:")
            for gc_target in entry.gc_targets:
                gc_targets_text.append(" ")
                gc_targets_text.append(sync_target_to_rich_text(gc_target))
            entry_tree.add(gc_targets_text)

            for entity_record in entry.entity_records:
                record_text = entity_tag_to_rich_text(entity_record.entity_tag)
                record_text.append(entity_id_to_rich_text(entity_record.ref_id))
                record_text.append(" ")
                record_text.append(
                    entity_summary_snippet_to_rich_text(entity_record.snippet)
                )
                entry_tree.add(record_text)

        console = Console()
        console.print(rich_tree)
