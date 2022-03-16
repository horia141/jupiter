"""A repository for project collections."""
import abc

from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.framework.repository import TrunkEntityRepository, TrunkEntityNotFoundError


class ProjectCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a project collection is not found."""


class ProjectCollectionRepository(TrunkEntityRepository[ProjectCollection], abc.ABC):
    """A repository of project collections."""
