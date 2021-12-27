"""The centralised point for interacting with Notion projects."""
from typing import ClassVar, Final

from domain.projects.infra.project_notion_manager import ProjectNotionManager, NotionProjectNotFoundError
from domain.projects.notion_project import NotionProject
from domain.workspaces.notion_workspace import NotionWorkspace
from framework.base.entity_id import EntityId
from remote.notion.common import NotionPageLink, NotionLockKey
from remote.notion.infra.pages_manager import PagesManager, NotionPageNotFoundError


class NotionProjectsManager(ProjectNotionManager):
    """The centralised point for interacting with Notion projects."""

    _KEY: ClassVar[str] = "projects"
    _PAGE_NAME: ClassVar[str] = "Projects"

    _pages_manager: Final[PagesManager]

    def __init__(self, pages_manager: PagesManager) -> None:
        """Constructor."""
        self._pages_manager = pages_manager

    def upsert_root_page(self, workspace: NotionWorkspace) -> None:
        """Upsert the root page of all projects."""
        self._pages_manager.upsert_page(NotionLockKey(self._KEY), self._PAGE_NAME, NotionPageLink(workspace.notion_id))

    def upsert_project(self, project: NotionProject) -> NotionProject:
        """Upsert a single project."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        project_page = \
            self._pages_manager.upsert_page(
                NotionLockKey(f"{self._KEY}:{project.ref_id}"), project.name, root_page)

        return NotionProject(name=str(project.name), ref_id=project.ref_id, notion_id=project_page.page_id)

    def save_project(self, project: NotionProject) -> NotionProject:
        """Save a project which already exists."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))

        try:
            self._pages_manager.save_page(NotionLockKey(f"{self._KEY}:{project.ref_id}"), project.name, root_page)
        except NotionPageNotFoundError as err:
            raise NotionProjectNotFoundError(f"Notion project with id {project.ref_id} could not be found") from err

        return project

    def load_project(self, ref_id: EntityId) -> NotionProject:
        """Load a project by its entity id."""
        try:
            project_page = self._pages_manager.get_page_extra(NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionPageNotFoundError as err:
            raise NotionProjectNotFoundError(f"Notion project with id {ref_id} could not be found") from err

        return NotionProject(name=project_page.name, ref_id=ref_id, notion_id=project_page.page_id)

    def remove_project(self, ref_id: EntityId) -> None:
        """Archive a project."""
        try:
            self._pages_manager.remove_page(NotionLockKey(f"{self._KEY}:{ref_id}"))
        except NotionPageNotFoundError as err:
            raise NotionProjectNotFoundError(f"Notion project with id {ref_id} could not be found") from err
