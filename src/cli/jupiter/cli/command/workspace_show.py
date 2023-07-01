"""UseCase for showing the workspace."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    project_to_rich_text,
)
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.workspaces.load import (
    WorkspaceLoadArgs,
    WorkspaceLoadUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class WorkspaceShow(LoggedInReadonlyCommand[WorkspaceLoadUseCase]):
    """UseCase class for showing the workspace."""

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

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            WorkspaceLoadArgs(),
        )

        rich_tree = Tree(f"⭐ {result.workspace.name}", guide_style="bold bright_blue")

        workspace_text = Text("Default ")
        workspace_text.append(project_to_rich_text(result.default_project.name))

        feature_flags_tree = Tree("Feature Flags:")
        for feature, flag in result.workspace.feature_flags.items():
            if flag:
                feature_flag_text = Text(f"✅ {feature}")
            else:
                feature_flag_text = Text(f"☑️ {feature}")
            feature_flags_tree.add(feature_flag_text)

        rich_tree.add(workspace_text)
        rich_tree.add(feature_flags_tree)

        console = Console()
        console.print(rich_tree)
