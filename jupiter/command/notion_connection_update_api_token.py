"""Usecase for updating the Notion API access token."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.remote.notion.api_token import NotionApiToken
from jupiter.use_cases.remote.notion.update_api_token import (
    NotionConnectionUpdateApiTokenUseCase,
)

LOGGER = logging.getLogger(__name__)


class NotionConnectionUpdateApiToken(command.Command):
    """Usecase for updating the Notion API access token."""

    _command: Final[NotionConnectionUpdateApiTokenUseCase]

    def __init__(self, the_command: NotionConnectionUpdateApiTokenUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "notion-connection-update-api-token"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Update the Notion API access token"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--api-token",
            dest="notion_api_token",
            required=False,
            help="The Notion API token",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        api_token = NotionApiToken.from_raw(args.notion_api_token)
        self._command.execute(
            NotionConnectionUpdateApiTokenUseCase.Args(api_token=api_token)
        )
