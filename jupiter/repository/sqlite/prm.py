"""SQLite based PRM database repositories."""
from typing import Optional, Iterable, List, Final

from sqlalchemy import select, MetaData, Table, Column, Integer, Boolean, DateTime, update, insert, \
    Unicode, String, delete
from sqlalchemy.engine import Result, Connection
from sqlalchemy.exc import IntegrityError

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.prm.infra.person_repository import PersonRepository, PersonAlreadyExistsError, PersonNotFoundError
from jupiter.domain.prm.infra.prm_database_repository import PrmDatabaseRepository, PrmDatabaseAlreadyExistsError, \
    PrmDatabaseNotFoundError
from jupiter.domain.prm.person import Person
from jupiter.domain.prm.person_birthday import PersonBirthday
from jupiter.domain.prm.person_name import PersonName
from jupiter.domain.prm.person_relationship import PersonRelationship
from jupiter.domain.prm.prm_database import PrmDatabase
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events


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
        try:
            result = self._connection.execute(insert(self._prm_database_table).values(
                ref_id=prm_database.ref_id.as_int() if prm_database.ref_id != BAD_REF_ID else None,
                archived=prm_database.archived,
                created_time=prm_database.created_time.to_db(),
                last_modified_time=prm_database.last_modified_time.to_db(),
                archived_time=prm_database.archived_time.to_db() if prm_database.archived_time else None,
                catch_up_project_ref_id=int(str(prm_database.catch_up_project_ref_id))))
        except IntegrityError as err:
            raise PrmDatabaseAlreadyExistsError(f"A PRM database already exists") from err
        prm_database.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._prm_database_event_table, prm_database)
        return prm_database

    def save(self, prm_database: PrmDatabase) -> PrmDatabase:
        """Save a PRM database - it should already exist."""
        result = self._connection.execute(
            update(self._prm_database_table)
            .where(self._prm_database_table.c.ref_id == prm_database.ref_id.as_int())
            .values(
                archived=prm_database.archived,
                created_time=prm_database.created_time.to_db(),
                last_modified_time=prm_database.last_modified_time.to_db(),
                archived_time=prm_database.archived_time.to_db() if prm_database.archived_time else None,
                catch_up_project_ref_id=prm_database.catch_up_project_ref_id.as_int()))
        if result.rowcount == 0:
            raise PrmDatabaseNotFoundError(f"The PRM database does not exist")
        upsert_events(self._connection, self._prm_database_event_table, prm_database)
        return prm_database

    def load(self) -> PrmDatabase:
        """Load the PRM database."""
        query_stmt = select(self._prm_database_table)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise PrmDatabaseNotFoundError(f"Missing PRM database")
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
            catch_up_project_ref_id=EntityId.from_raw(str(row["catch_up_project_ref_id"])))


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
            Column('catch_up_period', String, nullable=True),
            Column('catch_up_eisen', String, nullable=True),
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
                catch_up_eisen=person.catch_up_params.eisen.value if person.catch_up_params else None,
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
            raise PersonAlreadyExistsError(f"Person with name {person.name} already exists") from err
        person.assign_ref_id(EntityId.from_raw(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._person_event_table, person)
        return person

    def save(self, person: Person) -> Person:
        """Save a person - it should already exist."""
        result = self._connection.execute(
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
                catch_up_eisen=person.catch_up_params.eisen.value if person.catch_up_params else None,
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
        if result.rowcount == 0:
            raise PersonNotFoundError(f"A person with id {person.ref_id} does not exist")
        upsert_events(self._connection, self._person_event_table, person)
        return person

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Person:
        """Find a person by id."""
        query_stmt = select(self._person_table).where(self._person_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._person_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise PersonNotFoundError(f"Person identified by {ref_id} does not exist")
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
        if result is None:
            raise PersonNotFoundError(f"Person identified by {ref_id} does not exist")
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
            name=PersonName.from_raw(row["name"]),
            relationship=PersonRelationship.from_raw(row["relationship"]),
            catch_up_params=RecurringTaskGenParams(
                project_ref_id=EntityId.from_raw(str(row["catch_up_project_ref_id"])),
                period=RecurringTaskPeriod.from_raw(row["catch_up_period"]),
                eisen=Eisen.from_raw(row["catch_up_eisen"]),
                difficulty=Difficulty.from_raw(row["catch_up_difficulty"])
                if row["catch_up_difficulty"] else None,
                actionable_from_day=row["catch_up_actionable_from_day"],
                actionable_from_month=row["catch_up_actionable_from_month"],
                due_at_time=row["catch_up_due_at_time"],
                due_at_day=row["catch_up_due_at_day"],
                due_at_month=row["catch_up_due_at_month"])
            if row["catch_up_project_ref_id"] is not None and row["catch_up_period"] is not None else None,
            birthday=PersonBirthday.from_raw(row["birthday"]) if row["birthday"] else None)
