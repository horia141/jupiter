"""Command for initialising a workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from models.basic import BasicValidator

LOGGER = logging.getLogger(__name__)


class WorkspaceInit(command.Command):
    """Command class for initialising a workspace."""

    _basic_validator: Final[BasicValidator]
    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, basic_validator: BasicValidator, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "ws-init"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Initialise a workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", required=True, help="The plan name to use")
        parser.add_argument("--space-id", dest="workspace_space_id", required=True, help="The Notion space id to use")
        parser.add_argument("--token", dest="workspace_token", required=True, help="The Notion access token to use")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        name = self._basic_validator.entity_name_validate_and_clean(args.name)
        space_id = self._basic_validator.workspace_space_id_validate_and_clean(args.workspace_space_id)
        token = self._basic_validator.workspace_token_validate_and_clean(args.workspace_token)

        self._workspaces_controller.create_workspace(name, space_id, token)
