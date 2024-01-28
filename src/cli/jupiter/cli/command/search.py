"""Command for free form searching across all of Jupiter."""
from typing import cast

from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_summary_snippet_to_rich_text,
    entity_tag_to_rich_text,
)
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.use_cases.search import SearchResult, SearchUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class Search(LoggedInReadonlyCommand[SearchUseCase, SearchResult]):
    """Command for free form searching across all of Jupiter."""

    def _render_result(self, console: Console, context: AppLoggedInReadonlyUseCaseContext, result: SearchResult) -> None:
        result_page_text = Text(f"🚀 Showing {len(result.matches)} matches:")

        rich_tree = Tree(result_page_text, guide_style="bold bright_blue")

        for match in result.matches:
            match_text = Text("")
            match_text.append(entity_tag_to_rich_text(match.summary.entity_tag))
            match_text.append(entity_id_to_rich_text(match.summary.ref_id))
            match_text.append(" ")

            match_text.append(
                entity_summary_snippet_to_rich_text(match.summary.snippet)
            )

            if not match.summary.archived:
                modified_time_str = f"""Modified {(
                    match.summary.last_modified_time.as_datetime().diff_for_humans(
                        result.search_time.to_timestamp_at_end_of_day().as_datetime()
                    )
                )}"""
            else:
                modified_time_str = f"""Archived {(cast(Timestamp, match.summary.archived_time).as_datetime().diff_for_humans(
                    result.search_time.to_timestamp_at_end_of_day().as_datetime()
                ))}"""

            match_text.append(" [")
            match_text.append(modified_time_str)
            match_text.append("]")

            if match.summary.archived:
                match_text.stylize("gray62")

            rich_tree.add(match_text)

        console.print(rich_tree)
