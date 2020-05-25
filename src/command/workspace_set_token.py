"""Command for setting the access token of a workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class WorkspaceSetToken(command.Command):
    """Command class for setting the access token of a workspace."""

    _basic_validator: Final[BasicValidator]
    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, basic_validator: BasicValidator, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "ws-set-token"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the Notion access token of the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--token", dest="token", required=True, help="The plan name to use")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        token = self._basic_validator.workspace_token_validate_and_clean(args.token)
        self._workspaces_controller.set_workspace_token(token)
