"""Command for setting the access token of a workspace."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from domain.workspaces.notion_token import NotionToken

LOGGER = logging.getLogger(__name__)


class WorkspaceSetNotionToken(command.Command):
    """Command class for setting the access token of a workspace."""

    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-set-notion-token"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the Notion access token of the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--notion-token", dest="notion_token", required=True, help="The Notion token")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        notion_token = NotionToken.from_raw(args.notion_token)
        self._workspaces_controller.set_workspace_notion_token(notion_token)
