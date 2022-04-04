"""A repository for projects."""
import abc
from typing import Optional, Iterable, List

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class ProjectAlreadyExistsError(Exception):
    """Error raised when a project with the given key already exists."""


class ProjectNotFoundError(LeafEntityNotFoundError):
    """Error raised when a project is not found."""


class ProjectRepository(LeafEntityRepository[Project]):
    """A repository for projects."""

    @abc.abstractmethod
    def load_by_key(
        self, project_collection_ref_id: EntityId, key: ProjectKey
    ) -> Project:
        """Retrieve a particular project by its key."""

    @abc.abstractmethod
    def exchange_keys_for_ref_ids(
        self, project_keys: List[ProjectKey]
    ) -> List[EntityId]:
        """Exchange project keys for the respective project ids."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_keys: Optional[Iterable[ProjectKey]] = None,
    ) -> List[Project]:
        """Retrieve all the projects defined."""
