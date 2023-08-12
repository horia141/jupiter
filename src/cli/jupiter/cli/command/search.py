"""Command for free form searching across all of Jupiter."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_tag_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.search import SearchArgs, SearchUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class Search(LoggedInReadonlyCommand[SearchUseCase]):
    """Command for free form searching across all of Jupiter."""

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

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        filter_entity_tags = (
            [NamedEntityTag.from_raw(st) for st in args.filter_entity_tags]
            if len(args.filter_entity_tags) > 0
            else None
        )

        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            SearchArgs(
                query=args.query,
                limit=args.limit,
                include_archived=args.include_archived,
                filter_entity_tags=filter_entity_tags,
            ),
        )

        result_page_text = Text(
            f"🚀 Showing {len(result.matches)} matches out of {args.limit} asked:"
        )

        rich_tree = Tree(result_page_text, guide_style="bold bright_blue")

        for match in result.matches:
            match_text = Text("")
            match_text.append(entity_tag_to_rich_text(match.entity_tag))
            match_text.append(entity_id_to_rich_text(match.ref_id))
            match_text.append(" ")

            match_snippet_with_markup = match.match_snippet.replace(
                "found", "bold underline blue"
            )

            snippet_text = Text.from_markup(match_snippet_with_markup)
            match_text.append(snippet_text)

            if match.archived:
                match_text.stylize("gray62")

            rich_tree.add(match_text)

        console = Console()
        console.print(rich_tree)
