"""A repository for projects."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class ProjectNotFoundError(LeafEntityNotFoundError):
    """Error raised when a project is not found."""


class ProjectRepository(LeafEntityRepository[Project]):
    """A repository for projects."""

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Project]:
        """Retrieve all the projects defined."""
