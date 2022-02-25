"""The SQLite based vacations repository."""
from typing import Optional, Iterable, List, Final

from sqlalchemy import Table, Integer, Boolean, DateTime, ForeignKey, String, Column, MetaData, insert, update,\
    select, delete
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.infra.vacation_collection_repository import VacationCollectionNotFoundError, \
    VacationCollectionRepository
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository, VacationNotFoundError
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events, remove_events


class SqliteVacationCollectionRepository(VacationCollectionRepository):
    """The vacation collection repository."""

    _connection: Final[Connection]
    _vacation_collection_table: Final[Table]
    _vacation_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._vacation_collection_table = Table(
            'vacation_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'workspace_ref_id', Integer, ForeignKey("workspace.ref_id"), unique=True, index=True, nullable=False),
            keep_existing=True)
        self._vacation_collection_event_table = build_event_table(self._vacation_collection_table, metadata)

    def create(self, vacation_collection: VacationCollection) -> VacationCollection:
        """Create a vacation collection."""
        result = self._connection.execute(
            insert(self._vacation_collection_table).values(
                ref_id=vacation_collection.ref_id.as_int() if vacation_collection.ref_id != BAD_REF_ID else None,
                version=vacation_collection.version,
                archived=vacation_collection.archived,
                created_time=vacation_collection.created_time.to_db(),
                last_modified_time=vacation_collection.last_modified_time.to_db(),
                archived_time=vacation_collection.archived_time.to_db() if vacation_collection.archived_time else None,
                workspace_ref_id=vacation_collection.workspace_ref_id.as_int()))
        vacation_collection = vacation_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._vacation_collection_event_table, vacation_collection)
        return vacation_collection

    def save(self, vacation_collection: VacationCollection) -> VacationCollection:
        """Save a big vacation collection."""
        result = self._connection.execute(
            update(self._vacation_collection_table)
            .where(self._vacation_collection_table.c.ref_id == vacation_collection.ref_id.as_int())
            .values(
                version=vacation_collection.version,
                archived=vacation_collection.archived,
                created_time=vacation_collection.created_time.to_db(),
                last_modified_time=vacation_collection.last_modified_time.to_db(),
                archived_time=vacation_collection.archived_time.to_db() if vacation_collection.archived_time else None,
                workspace_ref_id=vacation_collection.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise VacationCollectionNotFoundError("The vacation collection does not exist")
        upsert_events(self._connection, self._vacation_collection_event_table, vacation_collection)
        return vacation_collection

    def load_by_workspace(self, workspace_ref_id: EntityId) -> VacationCollection:
        """Load a vacation collection for a given vacation."""
        query_stmt = \
            select(self._vacation_collection_table)\
                .where(self._vacation_collection_table.c.workspace_ref_id == workspace_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationCollectionNotFoundError(f"Big plan collection for vacation {workspace_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> VacationCollection:
        return VacationCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteVacationRepository(VacationRepository):
    """A repository for vacations."""

    _connection: Final[Connection]
    _vacation_table: Final[Table]
    _vacation_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._vacation_table = Table(
            'vacation',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('vacation_collection_ref_id', Integer, ForeignKey('vacation_collection.ref_id'), nullable=False),
            Column('name', String(100), nullable=False),
            Column('start_date', DateTime, nullable=False),
            Column('end_date', DateTime, nullable=False),
            keep_existing=True)
        self._vacation_event_table = build_event_table(self._vacation_table, metadata)

    def create(self, vacation: Vacation) -> Vacation:
        """Create a vacation."""
        result = self._connection.execute(
            insert(self._vacation_table).values(
                ref_id=vacation.ref_id.as_int() if vacation.ref_id != BAD_REF_ID else None,
                version=vacation.version,
                archived=vacation.archived,
                created_time=vacation.created_time.to_db(),
                last_modified_time=vacation.last_modified_time.to_db(),
                archived_time=vacation.archived_time.to_db() if vacation.archived_time else None,
                vacation_collection_ref_id=vacation.vacation_collection_ref_id.as_int(),
                name=str(vacation.name),
                start_date=vacation.start_date.to_db(),
                end_date=vacation.end_date.to_db()))
        vacation = vacation.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._vacation_event_table, vacation)
        return vacation

    def save(self, vacation: Vacation) -> Vacation:
        """Save a vacation."""
        result = self._connection.execute(
            update(self._vacation_table)
            .where(self._vacation_table.c.ref_id == vacation.ref_id.as_int())
            .values(
                version=vacation.version,
                archived=vacation.archived,
                created_time=vacation.created_time.to_db(),
                last_modified_time=vacation.last_modified_time.to_db(),
                archived_time=vacation.archived_time.to_db() if vacation.archived_time else None,
                vacation_collection_ref_id=vacation.vacation_collection_ref_id.as_int(),
                name=str(vacation.name),
                start_date=vacation.start_date.to_db(),
                end_date=vacation.end_date.to_db()))
        if result.rowcount == 0:
            raise VacationNotFoundError("The vacation does not exist")
        upsert_events(self._connection, self._vacation_event_table, vacation)
        return vacation

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Vacation:
        """Load a vacation."""
        query_stmt = select(self._vacation_table).where(self._vacation_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._vacation_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationNotFoundError(f"Vacation with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self, vacation_collection_ref_id: EntityId, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[Vacation]:
        """Retrieve all vacations."""
        query_stmt = \
            select(self._vacation_table)\
            .where(self._vacation_table.c.vacation_collection_ref_id == vacation_collection_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._vacation_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._vacation_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> None:
        """Remove a vacation."""
        query_stmt = select(self._vacation_table).where(self._vacation_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationNotFoundError(f"Vacation with id {ref_id} does not exist")
        remove_events(self._connection, self._vacation_event_table, ref_id)
        self._connection.execute(delete(self._vacation_table).where(self._vacation_table.c.ref_id == ref_id.as_int()))

    @staticmethod
    def _row_to_entity(row: Result) -> Vacation:
        return Vacation(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            vacation_collection_ref_id=EntityId.from_raw(str(row["vacation_collection_ref_id"])),
            name=VacationName.from_raw(row["name"]),
            start_date=ADate.from_db(row["start_date"]),
            end_date=ADate.from_db(row["end_date"]))
