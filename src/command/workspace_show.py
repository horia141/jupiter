"""Command for showing the workspace."""

import logging

import command.command as command
import repository.workspaces as workspaces

LOGGER = logging.getLogger(__name__)


class WorkspaceShow(command.Command):
    """Command class for showing the workspace."""

    @staticmethod
    def name():
        """The name of the command."""
        return "ws-show"

    @staticmethod
    def description():
        """The description of the command."""
        return "Show the current information about the workspace"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""

    def run(self, args):
        """Callback to execute when the command is invoked."""
        workspace_repository = workspaces.WorkspaceRepository()
        workspace = workspace_repository.load_workspace()

        # Dump out contents of workspace

        print(f'{workspace.name}')
