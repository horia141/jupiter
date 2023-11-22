"""Command for free form searching across all of Jupiter."""
from argparse import ArgumentParser, Namespace
from typing import Final, cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_tag_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search.search_limit import SearchLimit
from jupiter.core.domain.search.search_query import SearchQuery
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.search import SearchArgs, SearchUseCase
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class Search(LoggedInReadonlyCommand[SearchUseCase]):
    """Command for free form searching across all of Jupiter."""

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        use_case: SearchUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, top_level_context, use_case)
        self._global_properties = global_properties
        self._time_provider = time_provider

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "search"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Search"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--query",
            required=True,
            help="The search query for the title of entities to match",
        )
        parser.add_argument(
            "--limit",
            default=20,
            type=int,
            help="The maximum number of matches to return",
        )
        parser.add_argument(
            "--include-archived",
            dest="include_archived",
            default=False,
            action="store_true",
            help="Whether to include archived vacations or not",
        )
        parser.add_argument(
            "--entity",
            dest="filter_entity_tags",
            default=[],
            action="append",
            choices=[
                s.value
                for s in self._top_level_context.workspace.infer_entity_tags_for_enabled_features(
                    None
                )
            ],
            help="What types of entities to search",
        )
        parser.add_argument(
            "--created-after",
            dest="filter_created_time_after",
            help="Filter for entities created after this date",
        )
        parser.add_argument(
            "--created-before",
            dest="filter_created_time_before",
            help="Filter for entities created before this date",
        )
        parser.add_argument(
            "--last-modified-after",
            dest="filter_last_modified_time_after",
            help="Filter for entities last modified after this date",
        )
        parser.add_argument(
            "--last-modified-before",
            dest="filter_last_modified_time_before",
            help="Filter for entities last modified before this date",
        )
        parser.add_argument(
            "--archived-after",
            dest="filter_archived_time_after",
            help="Filter for entities archived after this date",
        )
        parser.add_argument(
            "--archived-before",
            dest="filter_archived_time_before",
            help="Filter for entities archived before this date",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        query = SearchQuery.from_raw(args.query)
        limit = SearchLimit.from_raw(args.limit)
        filter_entity_tags = (
            [NamedEntityTag.from_raw(st) for st in args.filter_entity_tags]
            if len(args.filter_entity_tags) > 0
            else None
        )
        filter_created_time_after = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_created_time_after
            )
            if args.filter_created_time_after
            else None
        )
        filter_created_time_before = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_created_time_before
            )
            if args.filter_created_time_before
            else None
        )
        filter_last_modified_time_after = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_last_modified_time_after
            )
            if args.filter_last_modified_time_after
            else None
        )
        filter_last_modified_time_before = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_last_modified_time_before
            )
            if args.filter_last_modified_time_before
            else None
        )
        filter_archived_time_after = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_archived_time_after
            )
            if args.filter_archived_time_after
            else None
        )
        filter_archived_time_before = (
            ADate.from_raw(
                self._global_properties.timezone, args.filter_archived_time_before
            )
            if args.filter_archived_time_before
            else None
        )

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SearchArgs(
                query=query,
                limit=limit,
                include_archived=args.include_archived,
                filter_entity_tags=filter_entity_tags,
                filter_created_time_after=filter_created_time_after,
                filter_created_time_before=filter_created_time_before,
                filter_last_modified_time_after=filter_last_modified_time_after,
                filter_last_modified_time_before=filter_last_modified_time_before,
                filter_archived_time_after=filter_archived_time_after,
                filter_archived_time_before=filter_archived_time_before,
            ),
        )

        result_page_text = Text(
            f"🚀 Showing {len(result.matches)} matches out of {args.limit} asked:"
        )

        rich_tree = Tree(result_page_text, guide_style="bold bright_blue")

        for match in result.matches:
            match_text = Text("")
            match_text.append(entity_tag_to_rich_text(match.summary.entity_tag))
            match_text.append(entity_id_to_rich_text(match.summary.ref_id))
            match_text.append(" ")

            match_snippet_with_markup = match.summary.snippet.replace(
                "found", "bold underline blue"
            )

            snippet_text = Text.from_markup(match_snippet_with_markup)
            match_text.append(snippet_text)

            if not match.summary.archived:
                modified_time_str = f"""Modified {(
                    match.summary.last_modified_time.as_datetime().diff_for_humans(
                        self._time_provider.get_current_time().as_datetime()
                    )
                )}"""
            else:
                modified_time_str = f"""Archived {(cast(Timestamp, match.summary.archived_time).as_datetime().diff_for_humans(
                    self._time_provider.get_current_time().as_datetime()
                ))}"""

            match_text.append(" [")
            match_text.append(modified_time_str)
            match_text.append("]")

            if match.summary.archived:
                match_text.stylize("gray62")

            rich_tree.add(match_text)

        console = Console()
        console.print(rich_tree)
