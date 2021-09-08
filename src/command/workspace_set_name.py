"""Command for setting the name of a workspace."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from domain.common.entity_name import EntityName

LOGGER = logging.getLogger(__name__)


class WorkspaceSetName(command.Command):
    """Command class for setting the name of a workspace."""

    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-set-name"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the name of the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--name", dest="name", required=True, help="The plan name to use")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        name = EntityName.from_raw(args.name)
        self._workspaces_controller.set_workspace_name(name)
