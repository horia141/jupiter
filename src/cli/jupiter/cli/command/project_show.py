"""UseCase for showing the projects."""

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from jupiter.core.use_cases.projects.find import ProjectFindResult, ProjectFindUseCase
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class ProjectShow(LoggedInReadonlyCommand[ProjectFindUseCase, ProjectFindResult]):
    """UseCase class for showing the projects."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: ProjectFindResult,
    ) -> None:
        sorted_projects = sorted(
            result.entries,
            key=lambda pe: (pe.project.archived, pe.project.created_time),
        )

        rich_tree = Tree("💡 Projects", guide_style="bold bright_blue")

        for entry in sorted_projects:
            project_text = Text("")
            project_text.append(entity_id_to_rich_text(entry.project.ref_id))
            project_text.append(" ")
            project_text.append(entity_name_to_rich_text(entry.project.name))

            if entry.project.archived:
                project_text.stylize("gray62")

            rich_tree.add(project_text)

        console.print(rich_tree)
