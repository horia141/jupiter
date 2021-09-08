"""Command for setting the timezone of a workspace."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from domain.common.timezone import Timezone

LOGGER = logging.getLogger(__name__)


class WorkspaceSetTimezone(command.Command):
    """Command class for setting the timezone of a workspace."""

    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-set-timezone"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the timezone of the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument("--timezone", required=True, help="The timezone use")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        timezone = Timezone.from_raw(args.timezone)
        self._workspaces_controller.set_workspace_timezone(timezone)
