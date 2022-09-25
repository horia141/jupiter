"""Usecase for updating the Notion connection token."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.use_cases.remote.notion.update_token import (
    NotionConnectionUpdateTokenUseCase,
)


class NotionConnectionUpdateToken(command.Command):
    """Usecase for updating the Notion connection token."""

    _command: Final[NotionConnectionUpdateTokenUseCase]

    def __init__(self, the_command: NotionConnectionUpdateTokenUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "notion-connection-update-token"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update the Notion connection token"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--token", dest="notion_token", required=False, help="The Notion token"
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        token = NotionToken.from_raw(args.notion_token)

        self._command.execute(
            progress_reporter, NotionConnectionUpdateTokenUseCase.Args(token=token)
        )
