"""A repository for projects."""
import abc
from typing import Optional, Iterable

from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from models.framework import EntityId


class ProjectRepository(abc.ABC):
    """A repository for projects."""

    @abc.abstractmethod
    def create(self, project: Project) -> Project:
        """Create a project."""

    @abc.abstractmethod
    def save(self, project: Project) -> Project:
        """Store a particular project with all new properties."""

    @abc.abstractmethod
    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Project:
        """Retrieve a particular project by its key."""

    @abc.abstractmethod
    def get_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all the projects defined."""
