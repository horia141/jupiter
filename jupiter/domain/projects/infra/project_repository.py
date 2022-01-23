"""A repository for projects."""
import abc
from typing import Optional, Iterable

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId


class ProjectAlreadyExistsError(Exception):
    """Error raised when a project with the given key already exists."""


class ProjectNotFoundError(Exception):
    """Error raised when a project is not found."""


class ProjectRepository(abc.ABC):
    """A repository for projects."""

    @abc.abstractmethod
    def create(self, project: Project) -> Project:
        """Create a project."""

    @abc.abstractmethod
    def save(self, project: Project) -> Project:
        """Store a particular project with all new properties."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Project:
        """Retrieve a particular project by its key."""

    @abc.abstractmethod
    def load_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all the projects defined."""
