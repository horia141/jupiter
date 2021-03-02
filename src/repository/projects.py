"""Repository for projects."""

from dataclasses import dataclass
import logging
import typing
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, Optional

from models.basic import EntityId, ProjectKey
from models.framework import RepositoryError
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, Eq, In
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class ProjectRow(BaseEntityRow):
    """A project."""

    key: ProjectKey
    name: str


@typing.final
class ProjectsRepository:
    """A repository for projects."""

    _PROJECTS_FILE_PATH: ClassVar[Path] = Path("./projects.yaml")

    _storage: Final[EntitiesStorage[ProjectRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[ProjectRow](self._PROJECTS_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'ProjectsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_project(self, key: ProjectKey, archived: bool, name: str) -> ProjectRow:
        """Create a project."""
        project_rows = self._storage.find_all(allow_archived=True, key=Eq(key))

        if len(project_rows) > 0:
            raise RepositoryError(f"Project with key='{key}' already exists")

        new_project_row = ProjectRow(key=key, archived=archived, name=name)
        return self._storage.create(new_project_row)

    def archive_project(self, ref_id: EntityId) -> ProjectRow:
        """Remove a particular project."""
        return self._storage.archive(ref_id)

    def update_project(self, new_project: ProjectRow) -> ProjectRow:
        """Store a particular project with all new properties."""
        return self._storage.update(new_project, archived_time_action=TimeFieldAction.DO_NOTHING)

    def load_project(self, ref_id: EntityId, allow_archived: bool = False) -> ProjectRow:
        """Retrieve a particular project by its key."""
        return self._storage.load(ref_id, allow_archived)

    def load_project_by_key(self, key: ProjectKey) -> ProjectRow:
        """Retrieve a particular project by its key."""
        return self._storage.find_first(allow_archived=False, key=Eq(key))

    def find_all_projects(
            self,
            allow_archived: bool = False,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[ProjectRow]:
        """Retrieve all the projects defined."""
        return self._storage.find_all(allow_archived=allow_archived, key=In(*filter_keys) if filter_keys else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "key": {"type": "string"},
            "name": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> ProjectRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return ProjectRow(
            key=ProjectKey(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=typing.cast(str, storage_form["name"]))

    @staticmethod
    def live_to_storage(live_form: ProjectRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "key": live_form.key,
            "name": live_form.name
        }
