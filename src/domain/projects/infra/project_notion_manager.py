"""The centralised point of interaction with projects on Notion-side."""
import abc

from domain.projects.notion_project import NotionProject
from domain.projects.project import Project
from domain.workspaces.notion_workspace import NotionWorkspace
from models.framework import EntityId


class ProjectNotionManager(abc.ABC):
    """The centralised point of interaction with projects on Notion-side."""

    @abc.abstractmethod
    def upsert_root_page(self, workspace: NotionWorkspace) -> None:
        """Upsert the root page of all projects."""

    @abc.abstractmethod
    def upsert(self, project: Project) -> NotionProject:
        """Upsert a single project."""

    @abc.abstractmethod
    def save(self, project: NotionProject) -> NotionProject:
        """Save a project which already exists."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId) -> NotionProject:
        """Load a project by its entity id."""

    @abc.abstractmethod
    def archive(self, project: Project) -> None:
        """Archive a project."""
