"""A repository for project collections."""
import abc

from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class ProjectCollectionRepository(TrunkEntityRepository[ProjectCollection], abc.ABC):
    """A repository of project collections."""
