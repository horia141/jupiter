"""Command for setting the default project of a workspace."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import command.command as command
from controllers.workspaces import WorkspacesController
from domain.projects.project_key import ProjectKey

LOGGER = logging.getLogger(__name__)


class WorkspaceSetDefaultProject(command.Command):
    """Command class for setting the default project of a workspace."""

    _workspaces_controller: Final[WorkspacesController]

    def __init__(self, workspaces_controller: WorkspacesController) -> None:
        """Constructor."""
        self._workspaces_controller = workspaces_controller

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-set-default-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the default project of the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--project", dest="project_key", required=False, help="The project key to mark as default")
        group.add_argument("--clear-project", dest="clear_project", default=False,
                           action="store_const", const=True, help="Clear the project")

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        if args.clear_project:
            project_key = None
        else:
            project_key = ProjectKey.from_raw(args.project_key)
        self._workspaces_controller.set_workspace_default_project(project_key)
