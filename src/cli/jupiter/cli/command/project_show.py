"""UseCase for showing the projects."""
from collections import defaultdict

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    entity_id_to_rich_text,
    entity_name_to_rich_text,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.concept.projects.find import (
    ProjectFindResult,
    ProjectFindResultEntry,
    ProjectFindUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
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
        if len(root) != 1:
            raise Exception("Root project not found.")
        self._render_project_tree(root[0], project_tree, root_rich_tree)

        console.print(root_rich_tree)

    def _render_project_tree(
        self,
        root: ProjectFindResultEntry,
        project_tree: defaultdict[EntityId | None, list[ProjectFindResultEntry]],
        tree: Tree,
    ) -> None:
        project_text = Text("")
        project_text.append(entity_id_to_rich_text(root.project.ref_id))
        project_text.append(" ")
        project_text.append(entity_name_to_rich_text(root.project.name))

        if root.project.archived:
            project_text.stylize("gray62")

        child_projects = project_tree[root.project.ref_id]
        sorted_child_projects = sorted(
            child_projects,
            key=lambda pe: (
                pe.project.archived,
                _index_in_list_or_none(
                    root.project.order_of_child_projects, pe.project.ref_id
                ),
                pe.project.created_time,
            ),
        )

        rich_project_tree = tree.add(project_text)

        for child_project in sorted_child_projects:
            self._render_project_tree(child_project, project_tree, rich_project_tree)


def _index_in_list_or_none(list_: list[EntityId], item: EntityId) -> int:
    try:
        return list_.index(item)
    except ValueError:
        return -1
