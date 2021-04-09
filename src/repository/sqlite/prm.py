"""SQLite based PRM database repositories."""
import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection
from typing import Optional, Iterable, List, Final, Iterator

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData
from sqlalchemy.future import Engine, create_engine

from domain.prm.infra.person_repository import PersonRepository
from domain.prm.infra.prm_database_repository import PrmDatabaseRepository
from domain.prm.infra.prm_engine import PrmUnitOfWork, PrmEngine
from domain.prm.person import Person
from domain.prm.prm_database import PrmDatabase
from models.basic import EntityId


class SqlitePrmDatabaseRepository(PrmDatabaseRepository):
    """A repository of PRM databases."""

    _connection: Final[Connection]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection

    def create(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Create a PRM database."""

    def save(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Save a PRM database - it should already exist."""

    def load(self) -> PrmDatabase:
        """Load the PRM database."""


class SqlitePersonRepository(PersonRepository):
    """A repository of persons."""

    _connection: Final[Connection]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection

    def create(self, person: Person) -> Person:
        """Create a person."""

    def save(self, person: Person) -> Person:
        """Save a person - it should already exist."""

    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Person:
        """Find a person by id."""

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[Person]:
        """Find all person matching some criteria."""

    def remove(self, ref_id: EntityId) -> Person:
        """Hard remove a person - an irreversible operation."""


class SqlitePrmUnitOfWork(PrmUnitOfWork):
    """A Sqlite specific PRM database unit of work."""

    _prm_database_repository: Final[SqlitePrmDatabaseRepository]
    _person_repository: Final[SqlitePersonRepository]

    def __init__(
            self, prm_database_repository: SqlitePrmDatabaseRepository,
            person_repository: SqlitePersonRepository) -> None:
        """Constructor."""
        self._prm_database_repository = prm_database_repository
        self._person_repository = person_repository

    @property
    def prm_database_repository(self) -> PrmDatabaseRepository:
        """The PRM database repository."""
        return self._prm_database_repository

    @property
    def person_repository(self) -> PersonRepository:
        """The person repository."""
        return self._person_repository


class SqlitePrmEngine(PrmEngine):
    """An Sqlite specific PRM database engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite PRM database engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_engine(config.sqlite_db_url, future=True, json_serializer=json.dumps)
        self._metadata = MetaData(bind=self._sql_engine)

    def prepare(self) -> None:
        """Prepare the environment for SQLite."""
        with self._sql_engine.begin() as connection:
            alembic_cfg = Config(str(self._config.alembic_ini_path))
            alembic_cfg.set_section_option('alembic', 'script_location', str(self._config.alembic_migrations_path))
            # pylint: disable=unsupported-assignment-operation
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, 'head')

    @contextmanager
    def get_unit_of_work(self) -> Iterator[PrmUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            prm_database_repository = SqlitePrmDatabaseRepository(connection, self._metadata)
            person_repository = SqlitePersonRepository(connection, self._metadata)
            yield SqlitePrmUnitOfWork(prm_database_repository, person_repository)
