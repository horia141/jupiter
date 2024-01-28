"""UseCase for showing the workspace."""

from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    project_to_rich_text,
)
from jupiter.core.use_cases.workspaces.load import (
    WorkspaceLoadResult,
    WorkspaceLoadUseCase,
)
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class WorkspaceShow(LoggedInReadonlyCommand[WorkspaceLoadUseCase, WorkspaceLoadResult]):
    """UseCase class for showing the workspace."""

    def _render_result(self, console: Console, context: AppLoggedInReadonlyUseCaseContext, result: WorkspaceLoadResult) -> None:
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

        console.print(rich_tree)
