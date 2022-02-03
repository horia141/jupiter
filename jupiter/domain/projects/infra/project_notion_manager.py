"""A manager of Notion-side projects."""
import abc
from typing import Iterable

from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionProjectNotFoundError(Exception):
    """Exception raised when a Notion project was not found."""


class ProjectNotionManager(abc.ABC):
    """A manager of Notion-side projects."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace, project_collection: NotionProjectCollection) -> None:
        """Upsert the root page structure for projects."""

    @abc.abstractmethod
    def upsert_project(self, project_collection_ref_id: EntityId, project: NotionProject) -> NotionProject:
        """Upsert a project on Notion-side."""

    @abc.abstractmethod
    def save_project(self, project_collection_ref_id: EntityId, project: NotionProject) -> NotionProject:
        """Upsert a project on Notion-side."""

    @abc.abstractmethod
    def load_project(self, project_collection_ref_id: EntityId, ref_id: EntityId) -> NotionProject:
        """Load a Notion-side project."""

    @abc.abstractmethod
    def load_all_projects(self, project_collection_ref_id: EntityId) -> Iterable[NotionProject]:
        """Load all Notion-side projects."""

    @abc.abstractmethod
    def remove_project(self, project_collection_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a project on Notion-side."""

    @abc.abstractmethod
    def drop_all_projects(self, project_collection_ref_id: EntityId) -> None:
        """Remove all projects on Notion-side."""

    @abc.abstractmethod
    def load_all_saved_project_ref_ids(self, project_collection_ref_id: EntityId) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_project_notion_ids(self, project_collection_ref_id: EntityId) -> Iterable[NotionId]:
        """Load ids of all projects we know about from Notion side."""

    @abc.abstractmethod
    def link_local_and_notion_entries(
            self, project_collection_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""
