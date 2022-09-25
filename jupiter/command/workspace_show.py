"""UseCase for showing the workspace."""
from argparse import ArgumentParser, Namespace
from typing import Final

from rich.console import Console
from rich.text import Text
from rich.tree import Tree

from jupiter.command import command
from jupiter.command.rendering import (
    project_to_rich_text,
    timezone_to_rich_text,
    RichConsoleProgressReporter,
)
from jupiter.use_cases.workspaces.find import WorkspaceFindUseCase


class WorkspaceShow(command.ReadonlyCommand):
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

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        result = self._command.execute(progress_reporter, WorkspaceFindUseCase.Args())

        rich_tree = Tree(f"⭐ {result.workspace.name}", guide_style="bold bright_blue")

        workspace_text = Text("")
        workspace_text.append(project_to_rich_text(result.default_project.name))
        workspace_text.append(" ")
        workspace_text.append(timezone_to_rich_text(result.workspace.timezone))

        rich_tree.add(workspace_text)

        console = Console()
        console.print(rich_tree)
