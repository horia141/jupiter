"""Repository for projects."""
import logging
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, Iterable, Optional

from framework.errors import RepositoryError
from framework.json import JSONDictType
from framework.entity_id import EntityId

from domain.entity_name import EntityName
from domain.projects.infra.project_engine import ProjectUnitOfWork, ProjectEngine
from domain.projects.infra.project_repository import ProjectRepository
from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from utils.storage import BaseEntityRow, EntitiesStorage, Eq, In
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _ProjectRow(BaseEntityRow):
    """A project."""

    key: ProjectKey
    name: EntityName


@typing.final
class YamlProjectRepository(ProjectRepository):
    """A repository for projects."""

    _PROJECTS_FILE_PATH: ClassVar[Path] = Path("./projects")
    _PROJECTS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_ProjectRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage = EntitiesStorage[_ProjectRow](
            self._PROJECTS_FILE_PATH, self._PROJECTS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlProjectRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, project: Project) -> Project:
        """Create a project."""
        project_rows = self._storage.find_all(allow_archived=True, key=Eq(project.key))

        if len(project_rows) > 0:
            raise RepositoryError(f"Project with key='{project.key}' already exists")

        new_project_row = _ProjectRow(key=project.key, archived=project.archived, name=project.name)
        new_project_row = self._storage.create(new_project_row)
        project.assign_ref_id(new_project_row.ref_id)
        return project

    def save(self, project: Project) -> Project:
        """Store a particular project with all new properties."""
        project_row = self._entity_to_row(project)
        project_row = self._storage.update(project_row)
        return self._row_to_entity(project_row)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Project:
        """Retrieve a particular project by its key."""
        return self._row_to_entity(self._storage.load(ref_id, allow_archived))

    def load_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""
        return self._row_to_entity(self._storage.find_first(allow_archived=False, key=Eq(key)))

    def find_all(
            self,
            allow_archived: bool = False,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all the projects defined."""
        return [self._row_to_entity(r) for r in
                self._storage.find_all(allow_archived=allow_archived, key=In(*filter_keys) if filter_keys else None)]

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "key": {"type": "string"},
            "name": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _ProjectRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _ProjectRow(
            key=ProjectKey.from_raw(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]),
            name=EntityName.from_raw(typing.cast(str, storage_form["name"])))

    @staticmethod
    def live_to_storage(live_form: _ProjectRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "key": str(live_form.key),
            "name": str(live_form.name)
        }

    @staticmethod
    def _entity_to_row(project: Project) -> _ProjectRow:
        project_row = _ProjectRow(
            archived=project.archived,
            key=project.key,
            name=project.name)
        project_row.ref_id = project.ref_id
        project_row.created_time = project.created_time
        project_row.archived_time = project.archived_time
        project_row.last_modified_time = project.last_modified_time
        return project_row

    @staticmethod
    def _row_to_entity(row: _ProjectRow) -> Project:
        return Project(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _key=row.key,
            _name=row.name)


class YamlProjectUnitOfWork(ProjectUnitOfWork):
    """The YAML storage unit of work."""

    _project_repository: Final[YamlProjectRepository]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Consturctor."""
        self._project_repository = YamlProjectRepository(time_provider)

    def __enter__(self) -> 'YamlProjectUnitOfWork':
        """Enter context."""
        self._project_repository.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def project_repository(self) -> ProjectRepository:
        """The projects repository."""
        return self._project_repository


class YamlProjectEngine(ProjectEngine):
    """The YAML storage engine."""

    _time_provider: Final[TimeProvider]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[ProjectUnitOfWork]:
        """Get the unit of work."""
        yield YamlProjectUnitOfWork(self._time_provider)
