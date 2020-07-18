"""Repository for projects."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, List, Optional

from models.basic import EntityId, ProjectKey, Timestamp, BasicValidator
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class Project:
    """A project."""

    ref_id: EntityId
    key: ProjectKey
    archived: bool
    name: str
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]


@typing.final
class ProjectsRepository:
    """A repository for projects."""

    _PROJECTS_FILE_PATH: ClassVar[Path] = Path("/data/projects.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[Project]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._PROJECTS_FILE_PATH, self)

    def __enter__(self) -> 'ProjectsRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
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
            name=name,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None)

        projects_next_idx += 1
        projects.append(new_project)

        self._structured_storage.save((projects_next_idx, projects))

        return new_project

    def archive_project(self, key: ProjectKey) -> Project:
        """Remove a particular project."""
        projects_next_idx, projects = self._structured_storage.load()

        for project in projects:
            if project.key == key:
                project.archived = True
                project.last_modified_time = self._time_provider.get_current_time()
                project.archived_time = self._time_provider.get_current_time()
                self._structured_storage.save((projects_next_idx, projects))
                return project

        raise RepositoryError(f"Project with key='{key}' does not exist")

    def load_all_projects(
            self,
            filter_archived: bool = True,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all the projects defined."""
        _, projects = self._structured_storage.load()
        filter_keys_set = frozenset(filter_keys) if filter_keys else []
        return [p for p in projects
                if (filter_archived is False or p.archived is False)
                and (len(filter_keys_set) == 0 or p.key in filter_keys_set)]

    def load_project(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""
        _, projects = self._structured_storage.load()
        found_project = self._find_project_by_key(key, projects)
        if not found_project:
            raise RepositoryError(f"Project with key='{key}' does not exist")
        if found_project.archived:
            raise RepositoryError(f"Project with key='{key}' is archived")
        return found_project

    def save_project(self, new_project: Project) -> Project:
        """Store a particular project with all new properties."""
        projects_next_idx, projects = self._structured_storage.load()

        if not self._find_project_by_key(new_project.key, projects):
            raise RepositoryError(f"Project with key='{new_project.key}' does not exist")

        new_project.last_modified_time = self._time_provider.get_current_time()
        new_projects = [(p if p.ref_id != new_project.ref_id else new_project) for p in projects]
        self._structured_storage.save((projects_next_idx, new_projects))

        return new_project

    @staticmethod
    def _find_project_by_key(key: ProjectKey, projects: List[Project]) -> Optional[Project]:
        try:
            return next(p for p in projects if p.key == key)
        except StopIteration:
            return None

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "key": {"type": "string"},
                "archived": {"type": "boolean"},
                "name": {"type": "string"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> Project:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return Project(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            key=ProjectKey(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=typing.cast(str, storage_form["name"]),
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] is not None else None)

    @staticmethod
    def live_to_storage(live_form: Project) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "key": live_form.key,
            "archived": live_form.archived,
            "name": live_form.name,
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time),
            "archived_time": BasicValidator.timestamp_to_str(live_form.archived_time)
                             if live_form.archived_time else None
        }
