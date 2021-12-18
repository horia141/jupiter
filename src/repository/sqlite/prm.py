"""SQLite based PRM database repositories."""
import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable, List, Final, Iterator

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, MetaData, Table, Column, Integer, Boolean, DateTime, update, insert, \
    Unicode, String, JSON, delete
from sqlalchemy.engine import Result, Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Engine

from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.timestamp import Timestamp
from domain.prm.infra.person_repository import PersonRepository
from domain.prm.infra.prm_database_repository import PrmDatabaseRepository
from domain.prm.infra.prm_engine import PrmUnitOfWork, PrmEngine
from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.prm.prm_database import PrmDatabase
from models.errors import RepositoryError
from models.framework import EntityId, BAD_REF_ID
from repository.sqlite.events import build_event_table, upsert_events
from utils.storage import StructuredStorageError


class SqlitePrmDatabaseRepository(PrmDatabaseRepository):
    """A repository of PRM databases."""

    _connection: Final[Connection]
    _prm_database_table: Final[Table]
    _prm_database_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._prm_database_table = Table(
            'prm_database',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('catch_up_project_ref_id', Integer, nullable=True),
            keep_existing=True)
        self._prm_database_event_table = build_event_table(self._prm_database_table, metadata)

    def create(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Create a PRM database."""
        result = self._connection.execute(insert(self._prm_database_table).values(
            ref_id=prm_database.ref_id.as_int() if prm_database.ref_id != BAD_REF_ID else None,
            archived=prm_database.archived,
            created_time=prm_database.created_time.to_db(),
            last_modified_time=prm_database.last_modified_time.to_db(),
            archived_time=prm_database.archived_time.to_db() if prm_database.archived_time else None,
            catch_up_project_ref_id=int(str(prm_database.catch_up_project_ref_id))))
        prm_database.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._prm_database_event_table, prm_database)
        return prm_database

    def save(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Save a PRM database - it should already exist."""
        self._connection.execute(
            update(self._prm_database_table)
            .where(self._prm_database_table.c.ref_id == prm_database.ref_id.as_int())
            .values(
                archived=prm_database.archived,
                created_time=prm_database.created_time.to_db(),
                last_modified_time=prm_database.last_modified_time.to_db(),
                archived_time=prm_database.archived_time.to_db() if prm_database.archived_time else None,
                catch_up_project_ref_id=prm_database.catch_up_project_ref_id.as_int()))
        upsert_events(self._connection, self._prm_database_event_table, prm_database)
        return prm_database

    def find(self) -> PrmDatabase:
        """Load the PRM database."""
        query_stmt = select(self._prm_database_table)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise StructuredStorageError(f"Missing PRM database")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> PrmDatabase:
        return PrmDatabase(
            _ref_id=EntityId.from_raw(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=Timestamp.from_db(row["created_time"]),
            _archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            _events=[],
            _catch_up_project_ref_id=EntityId.from_raw(str(row["catch_up_project_ref_id"])))


class SqlitePersonRepository(PersonRepository):
    """A repository of persons."""

    _connection: Final[Connection]
    _person_table: Final[Table]
    _person_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._person_table = Table(
            'person',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('name', Unicode(), nullable=False),
            Column('relationship', String(), nullable=False),
            Column('catch_up_project_ref_id', Integer, nullable=True),
            Column('catch_up_period', String(), nullable=True),
            Column('catch_up_eisen', JSON, nullable=True),
            Column('catch_up_difficulty', String, nullable=True),
            Column('catch_up_actionable_from_day', Integer, nullable=True),
            Column('catch_up_actionable_from_month', Integer, nullable=True),
            Column('catch_up_due_at_time', String, nullable=True),
            Column('catch_up_due_at_day', Integer, nullable=True),
            Column('catch_up_due_at_month', Integer, nullable=True),
            Column('birthday', String(), nullable=True),
            keep_existing=True)
        self._person_event_table = build_event_table(self._person_table, metadata)

    def create(self, person: Person) -> Person:
        """Create a person."""
        try:
            result = self._connection.execute(insert(self._person_table).values(
                ref_id=person.ref_id.as_int() if person.ref_id != BAD_REF_ID else None,
                archived=person.archived,
                created_time=person.created_time.to_db(),
                last_modified_time=person.last_modified_time.to_db(),
                archived_time=person.archived_time.to_db() if person.archived_time else None,
                name=str(person.name),
                relationship=person.relationship.value,
                catch_up_project_ref_id=
                person.catch_up_params.project_ref_id.as_int() if person.catch_up_params else None,
                catch_up_period=person.catch_up_params.period.value if person.catch_up_params else None,
                catch_up_eisen=[e.value for e in person.catch_up_params.eisen] if person.catch_up_params else [],
                catch_up_difficulty=person.catch_up_params.difficulty.value
                if person.catch_up_params and person.catch_up_params.difficulty else None,
                catch_up_actionable_from_day=person.catch_up_params.actionable_from_day
                if person.catch_up_params else None,
                catch_up_actionable_from_month=person.catch_up_params.actionable_from_month
                if person.catch_up_params else None,
                catch_up_due_at_time=person.catch_up_params.due_at_time if person.catch_up_params else None,
                catch_up_due_at_day=person.catch_up_params.due_at_day if person.catch_up_params else None,
                catch_up_due_at_month=person.catch_up_params.due_at_month if person.catch_up_params else None,
                birthday=str(person.birthday) if person.birthday else None))
        except IntegrityError as err:
            raise RepositoryError(f"Person with name='{person.name}' already exists") from err
        person.assign_ref_id(EntityId.from_raw(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._person_event_table, person)
        return person

    def save(self, person: Person) -> Person:
        """Save a person - it should already exist."""
        self._connection.execute(
            update(self._person_table)
            .where(self._person_table.c.ref_id == person.ref_id.as_int())
            .values(
                archived=person.archived,
                created_time=person.created_time.to_db(),
                last_modified_time=person.last_modified_time.to_db(),
                archived_time=person.archived_time.to_db() if person.archived_time else None,
                name=str(person.name),
                relationship=person.relationship.value,
                catch_up_project_ref_id=person.catch_up_params.project_ref_id.as_int()
                if person.catch_up_params else None,
                catch_up_period=person.catch_up_params.period.value if person.catch_up_params else None,
                catch_up_eisen=[e.value for e in person.catch_up_params.eisen] if person.catch_up_params else [],
                catch_up_difficulty=person.catch_up_params.difficulty.value
                if person.catch_up_params and person.catch_up_params.difficulty else None,
                catch_up_actionable_from_day=person.catch_up_params.actionable_from_day
                if person.catch_up_params else None,
                catch_up_actionable_from_month=person.catch_up_params.actionable_from_month
                if person.catch_up_params else None,
                catch_up_due_at_time=person.catch_up_params.due_at_time if person.catch_up_params else None,
                catch_up_due_at_day=person.catch_up_params.due_at_day if person.catch_up_params else None,
                catch_up_due_at_month=person.catch_up_params.due_at_month if person.catch_up_params else None,
                birthday=str(person.birthday) if person.birthday else None))
        upsert_events(self._connection, self._person_event_table, person)
        return person

    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Person:
        """Find a person by id."""
        query_stmt = select(self._person_table).where(self._person_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise StructuredStorageError(f"Person identified by {ref_id} does not exist or is archived")
        return self._row_to_entity(result)

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[Person]:
        """Find all person matching some criteria."""
        query_stmt = select(self._person_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._person_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Person:
        """Hard remove a person - an irreversible operation."""
        query_stmt = select(self._person_table).where(self._person_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        self._connection.execute(delete(self._person_table).where(self._person_table.c.ref_id == ref_id.as_int()))
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Person:
        return Person(
            _ref_id=EntityId(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=Timestamp.from_db(row["created_time"]),
            _archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            _events=[],
            _name=EntityName.from_raw(row["name"]),
            _relationship=PersonRelationship.from_raw(row["relationship"]),
            _catch_up_params=RecurringTaskGenParams(
                project_ref_id=EntityId.from_raw(str(row["catch_up_project_ref_id"])),
                period=RecurringTaskPeriod.from_raw(row["catch_up_period"]),
                eisen=[Eisen.from_raw(e) for e in row["catch_up_eisen"]],
                difficulty=Difficulty.from_raw(row["catch_up_difficulty"])
                if row["catch_up_difficulty"] else None,
                actionable_from_day=row["catch_up_actionable_from_day"],
                actionable_from_month=row["catch_up_actionable_from_month"],
                due_at_time=row["catch_up_due_at_time"],
                due_at_day=row["catch_up_due_at_day"],
                due_at_month=row["catch_up_due_at_month"])
            if row["catch_up_project_ref_id"] is not None and row["catch_up_period"] is not None else None,
            _birthday=PersonBirthday.from_raw(row["birthday"]) if row["birthday"] else None)


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
