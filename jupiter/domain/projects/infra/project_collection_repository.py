"""A repository for project collections."""
import abc

from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class ProjectCollectionNotFoundError(Exception):
    """Error raised when a project collection is not found."""


class ProjectCollectionRepository(Repository, abc.ABC):
    """A repository of project collections."""

    @abc.abstractmethod
    def create(self, project_collection: ProjectCollection) -> ProjectCollection:
        """Create a project collection."""

    @abc.abstractmethod
    def save(self, project_collection: ProjectCollection) -> ProjectCollection:
        """Save a project collection."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> ProjectCollection:
        """Retrieve a project collection by its owning workspace id."""
