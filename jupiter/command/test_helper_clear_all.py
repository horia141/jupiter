"""Test helper command for clearing all branch and leaf entities."""
import logging
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.command import command
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.use_cases.test_helper.clear_all import ClearAllUseCase

LOGGER = logging.getLogger(__name__)


class TestHelperClearAll(command.TestHelperCommand):
    """Test helper command for clearing all branch and leaf entities."""

    _command: Final[ClearAllUseCase]

    def __init__(self, the_command: ClearAllUseCase) -> None:
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "test-helper-clear-all"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Clear all the data in the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--workspace-name",
            required=True,
            dest="workspace_name",
            help="The workspace name to use",
        )
        parser.add_argument(
            "--workspace-timezone",
            required=True,
            dest="workspace_timezone",
            help="The timezone you're currently in",
        )
        parser.add_argument(
            "--default-project",
            dest="default_project_key",
            required=False,
            help="The project key to use as a general default",
        )

    def run(self, args: Namespace) -> None:
        """Callback to execute when the command is invoked."""
        workspace_name = WorkspaceName.from_raw(args.workspace_name)
        workspace_timezone = Timezone.from_raw(args.workspace_timezone)
        default_project_key = ProjectKey.from_raw(args.default_project_key)
        self._command.execute(
            ClearAllUseCase.Args(
                workspace_name=workspace_name,
                workspace_timezone=workspace_timezone,
                default_project_key=default_project_key,
            )
        )
