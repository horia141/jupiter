"""UseCase for showing the projects."""

from collections import defaultdict

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from jupiter.core.use_cases.projects.find import (
    ProjectFindResult,
    ProjectFindResultEntry,
    ProjectFindUseCase,
)
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
        project_tree: defaultdict[
            EntityId | None, list[ProjectFindResultEntry]
        ] = defaultdict(list)
        for entry in result.entries:
            project_tree[entry.project.parent_project_ref_id].append(entry)

        root_rich_tree = Tree("💡 Projects", guide_style="bold bright_blue")

        root = project_tree[None]
        self._render_project_tree(root, project_tree, root_rich_tree)

        console.print(root_rich_tree)

    def _render_project_tree(
        self,
        projects: list[ProjectFindResultEntry],
        project_tree: defaultdict[EntityId | None, list[ProjectFindResultEntry]],
        tree: Tree,
    ) -> None:
        sorted_projects = sorted(
            projects,
            key=lambda pe: (pe.project.archived, pe.project.created_time),
        )

        for entry in sorted_projects:
            project_text = Text("")
            project_text.append(entity_id_to_rich_text(entry.project.ref_id))
            project_text.append(" ")
            project_text.append(entity_name_to_rich_text(entry.project.name))

            if entry.project.archived:
                project_text.stylize("gray62")

            child_tree = tree.add(project_text)

            self._render_project_tree(
                project_tree[entry.project.ref_id], project_tree, child_tree
            )
