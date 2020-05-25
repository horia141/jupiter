"""Repository for projects."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from typing import Final, Any, Dict, ClassVar, Iterable, List, Optional

from models.basic import EntityId, ProjectKey
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage

LOGGER = logging.getLogger(__name__)


@typing.final
@dataclass()
class Project:
    """A project."""

    ref_id: EntityId
    key: ProjectKey
    archived: bool
    name: str


@typing.final
class ProjectsRepository:
    """A repository for projects."""

    _PROJECTS_FILE_PATH: ClassVar[Path] = Path("/data/projects.yaml")

    _structured_storage: Final[StructuredCollectionStorage[Project]]

    def __init__(self) -> None:
        """Constructor."""
        self._structured_storage = StructuredCollectionStorage(self._PROJECTS_FILE_PATH, self)

    def __enter__(self) -> 'ProjectsRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_project(self, key: ProjectKey, archived: bool, name: str) -> Project:
        """Create a project."""
        projects_next_idx, projects = self._structured_storage.load()

        if self._find_project_by_key(key, projects):
            raise RepositoryError(f"Project with key='{key}' already exists")

        new_project = Project(
            ref_id=EntityId(str(projects_next_idx)),
            key=key,
            archived=archived,
            name=name)

        projects_next_idx += 1
        projects.append(new_project)

        self._structured_storage.save((projects_next_idx, projects))

        return new_project

    def remove_project_by_key(self, key: ProjectKey) -> Project:
        """Remove a particular project."""
        projects_next_idx, projects = self._structured_storage.load()

        for project in projects:
            if project.key == key:
                project.archived = True
                self._structured_storage.save((projects_next_idx, projects))
                return project

        raise RepositoryError(f"Project with key='{key}' does not exist")

    def list_all_projects(
            self,
            filter_archived: bool = True,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all the projects defined."""
        _, projects = self._structured_storage.load()
        filter_keys_set = frozenset(filter_keys) if filter_keys else []
        return [p for p in projects
                if (filter_archived is False or p.archived is False)
                and (len(filter_keys_set) == 0 or p.key in filter_keys_set)]

    def load_project_by_id(self, ref_id: EntityId) -> Project:
        """Retrieve a particular project by its key."""
        _, projects = self._structured_storage.load()
        found_project = self._find_project_by_id(ref_id, projects)
        if not found_project:
            raise RepositoryError(f"Project with id='{ref_id}' does not exist")
        if found_project.archived:
            raise RepositoryError(f"Project with id='{ref_id}' is archived")
        return found_project

    def load_project_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""
        _, projects = self._structured_storage.load()
        found_project = self._find_project_by_key(key, projects)
        if not found_project:
            raise RepositoryError(f"Project with key='{key}' does not exist")
        if found_project.archived:
            raise RepositoryError(f"Project with key='{key}' is archived")
        return found_project

    def save_project(self, new_project: Project) -> None:
        """Store a particular project with all new properties."""
        projects_next_idx, projects = self._structured_storage.load()

        if not self._find_project_by_key(new_project.key, projects):
            raise RepositoryError(f"Project with key='{new_project.key}' does not exist")

        new_projects = [(p if p.ref_id != new_project.ref_id else new_project) for p in projects]
        self._structured_storage.save((projects_next_idx, new_projects))

    @staticmethod
    def _find_project_by_id(ref_id: EntityId, projects: List[Project]) -> Optional[Project]:
        try:
            return next(p for p in projects if p.ref_id == ref_id)
        except StopIteration:
            return None

    @staticmethod
    def _find_project_by_key(key: ProjectKey, projects: List[Project]) -> Optional[Project]:
        try:
            return next(p for p in projects if p.key == key)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> Dict[str, Any]:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "key": {"type": "string"},
                "archived": {"type": "boolean"},
                "name": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: Any) -> Project:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Project(
            ref_id=EntityId(storage_form["ref_id"]),
            key=ProjectKey(storage_form["key"]),
            archived=storage_form["archived"],
            name=storage_form["name"])

    @staticmethod
    def live_to_storage(live_form: Project) -> Any:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "key": live_form.key,
            "archived": live_form.archived,
            "name": live_form.name
        }
