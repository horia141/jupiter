"""The centralised point for interacting with Notion projects."""
from dataclasses import dataclass
from typing import ClassVar, Final

from models.framework import EntityId
from remote.notion.common import NotionPageLink, NotionLockKey, NotionId
from remote.notion.infra.pages_manager import PagesManager


@dataclass()
class ProjectNotionPage:
    """A project on Notion side."""

    name: str
    ref_id: EntityId
    notion_id: NotionId


class NotionProjectsManager:
    """The centralised point for interacting with Notion projects."""

    _KEY: ClassVar[str] = "projects"
    _PAGE_NAME: ClassVar[str] = "Projects"

    _pages_manager: Final[PagesManager]

    def __init__(self, pages_manager: PagesManager) -> None:
        """Constructor."""
        self._pages_manager = pages_manager

    def upsert_root_page(self, parent_page_link: NotionPageLink) -> None:
        """Upsert the root page for the projects section."""
        self._pages_manager.upsert_page(NotionLockKey(self._KEY), self._PAGE_NAME, parent_page_link)

    def upsert_project(self, ref_id: EntityId, name: str) -> ProjectNotionPage:
        """Upsert the Notion-side project."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        project_page = self._pages_manager.upsert_page(NotionLockKey(f"{self._KEY}:{ref_id}"), name, root_page)

        return ProjectNotionPage(name=name, ref_id=ref_id, notion_id=project_page.page_id)

    def archive_project(self, ref_id: EntityId) -> None:
        """Archive the Notion-side project."""
        self._pages_manager.remove_page(NotionLockKey(f"{self._KEY}:{ref_id}"))

    def load_project(self, ref_id: EntityId) -> ProjectNotionPage:
        """Load a project from Notion."""
        project_page = self._pages_manager.get_page_extra(NotionLockKey(f"{self._KEY}:{ref_id}"))
        return ProjectNotionPage(name=project_page.name, ref_id=ref_id, notion_id=project_page.page_id)

    def save_project(self, project_page: ProjectNotionPage) -> ProjectNotionPage:
        """Save a project to Notion - just the pages structure."""
        root_page = self._pages_manager.get_page(NotionLockKey(self._KEY))
        new_project_page = self._pages_manager.upsert_page(NotionLockKey(
            f"{self._KEY}:{project_page.ref_id}"), project_page.name, root_page)
        return ProjectNotionPage(
            name=project_page.name, ref_id=project_page.ref_id, notion_id=new_project_page.page_id)
