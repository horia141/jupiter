"""Command for syncing the workspace info from Notion."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from models.basic import BasicValidator, SyncPrefer

LOGGER = logging.getLogger(__name__)


class WorkspaceSync(command.Command):
    """Command class for syncing the workspace info from Notion."""

    _basic_validator: Final[BasicValidator]
    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, basic_validator: BasicValidator, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "ws-sync"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Synchronises Notion and the local storage"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--prefer", dest="sync_prefer", choices=BasicValidator.sync_prefer_values(),
                            default=SyncPrefer.LOCAL.value, help="Which source to prefer")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        sync_prefer = self._basic_validator.sync_prefer_validate_and_clean(args.sync_prefer)
        self._workspaces_controller.workspace_sync(sync_prefer)
