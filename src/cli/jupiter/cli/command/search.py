"""Command for free form searching across all of Jupiter."""
from argparse import ArgumentParser, Namespace
from typing import Final, cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_summary_snippet_to_rich_text,
    entity_tag_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search.search_limit import SearchLimit
from jupiter.core.domain.search.search_query import SearchQuery
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.search import SearchArgs, SearchResult, SearchUseCase
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class Search(LoggedInReadonlyCommand[SearchUseCase]):
    """Command for free form searching across all of Jupiter."""

    def _render_result(self, console: Console, result: SearchResult) -> None:
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
                        result.search_time.to_db()
                    )
                )}"""
            else:
                modified_time_str = f"""Archived {(cast(Timestamp, match.summary.archived_time).as_datetime().diff_for_humans(
                    result.search_time.to_db()
                ))}"""

            match_text.append(" [")
            match_text.append(modified_time_str)
            match_text.append("]")

            if match.summary.archived:
                match_text.stylize("gray62")

            rich_tree.add(match_text)

        console.print(rich_tree)
