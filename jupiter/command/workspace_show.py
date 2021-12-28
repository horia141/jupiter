"""UseCase for showing the workspace."""

import logging
from argparse import ArgumentParser, Namespace
from typing import Final

import jupiter.command.command as command
from jupiter.use_cases.workspaces.find import WorkspaceFindUseCase

LOGGER = logging.getLogger(__name__)


class WorkspaceShow(command.Command):
    """UseCase class for showing the workspace."""

    _command: Final[WorkspaceFindUseCase]

    def __init__(self, the_command: WorkspaceFindUseCase) -> None:
        """Constructor."""
        self._command = the_command

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
        response = self._command.execute(None)
        print(f'{response.workspace.name} timezone={response.workspace.timezone}' +
              (f' default project is "{response.default_project.name}"' if response.default_project else ''))
