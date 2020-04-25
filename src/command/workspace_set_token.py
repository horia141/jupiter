"""Command for setting the access token of a workspace."""

import logging

import command.command as command
from models.basic import BasicValidator
import repository.workspaces as workspaces

LOGGER = logging.getLogger(__name__)


class WorkspaceSetToken(command.Command):
    """Command class for setting the access token of a workspace."""

    @staticmethod
    def name():
        """The name of the command."""
        return "ws-set-token"

    @staticmethod
    def description():
        """The description of the command."""
        return "Change the Notion access token of the workspace"

    def build_parser(self, parser):
        """Construct a argparse parser for the command."""
        parser.add_argument("--token", dest="workspace_token", required=True, help="The plan name to use")

    def run(self, args):
        """Callback to execute when the command is invoked."""
        basic_validator = BasicValidator()

        # Parse arguments
        token = basic_validator.workspace_token_validate_and_clean(args.token)

        workspace_repository = workspaces.WorkspaceRepository()
        workspace = workspace_repository.load_workspace()

        workspace.token = token
        workspace_repository.save_workspace(workspace)
