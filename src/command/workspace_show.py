"""Command for showing the workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController

LOGGER = logging.getLogger(__name__)


class WorkspaceShow(command.Command):
    """Command class for showing the workspace."""

    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-show"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Show the current information about the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        workspace = self._workspaces_controller.load_workspace()
        print(f'{workspace.name}')
