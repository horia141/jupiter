"""The SQLite based vacations repository."""
from typing import Optional, Iterable, List, Final

from sqlalchemy import (
    Table,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Column,
    MetaData,
    insert,
    update,
    select,
    delete,
)
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionNotFoundError,
    VacationCollectionRepository,
)
from jupiter.domain.vacations.infra.vacation_repository import (
    VacationRepository,
    VacationNotFoundError,
)
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import (
    build_event_table,
    upsert_events,
    remove_events,
)


class SqliteVacationCollectionRepository(VacationCollectionRepository):
    """The vacation collection repository."""

    _connection: Final[Connection]
    _vacation_collection_table: Final[Table]
    _vacation_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._vacation_collection_table = Table(
            "vacation_collection",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "workspace_ref_id",
                Integer,
                ForeignKey("workspace.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            keep_existing=True,
        )
        self._vacation_collection_event_table = build_event_table(
            self._vacation_collection_table, metadata
        )

    def create(self, entity: VacationCollection) -> VacationCollection:
        """Create a vacation collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._vacation_collection_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._vacation_collection_event_table, entity)
        return entity

    def save(self, entity: VacationCollection) -> VacationCollection:
        """Save a big vacation collection."""
        result = self._connection.execute(
            update(self._vacation_collection_table)
            .where(self._vacation_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            )
        )
        if result.rowcount == 0:
            raise VacationCollectionNotFoundError(
                "The vacation collection does not exist"
            )
        upsert_events(self._connection, self._vacation_collection_event_table, entity)
        return entity

    def load_by_parent(self, parent_ref_id: EntityId) -> VacationCollection:
        """Load a vacation collection for a given vacation."""
        query_stmt = select(self._vacation_collection_table).where(
            self._vacation_collection_table.c.workspace_ref_id == parent_ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationCollectionNotFoundError(
                f"Vacation collection for workspace {parent_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> VacationCollection:
        return VacationCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])),
        )


class SqliteVacationRepository(VacationRepository):
    """A repository for vacations."""

    _connection: Final[Connection]
    _vacation_table: Final[Table]
    _vacation_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._vacation_table = Table(
            "vacation",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "vacation_collection_ref_id",
                Integer,
                ForeignKey("vacation_collection.ref_id"),
                nullable=False,
            ),
            Column("name", String(100), nullable=False),
            Column("start_date", DateTime, nullable=False),
            Column("end_date", DateTime, nullable=False),
            keep_existing=True,
        )
        self._vacation_event_table = build_event_table(self._vacation_table, metadata)

    def create(self, entity: Vacation) -> Vacation:
        """Create a vacation."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._vacation_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                vacation_collection_ref_id=entity.vacation_collection_ref_id.as_int(),
                name=str(entity.name),
                start_date=entity.start_date.to_db(),
                end_date=entity.end_date.to_db(),
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._vacation_event_table, entity)
        return entity

    def save(self, entity: Vacation) -> Vacation:
        """Save a vacation."""
        result = self._connection.execute(
            update(self._vacation_table)
            .where(self._vacation_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                vacation_collection_ref_id=entity.vacation_collection_ref_id.as_int(),
                name=str(entity.name),
                start_date=entity.start_date.to_db(),
                end_date=entity.end_date.to_db(),
            )
        )
        if result.rowcount == 0:
            raise VacationNotFoundError("The vacation does not exist")
        upsert_events(self._connection, self._vacation_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Vacation:
        """Load a vacation."""
        query_stmt = select(self._vacation_table).where(
            self._vacation_table.c.ref_id == ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._vacation_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationNotFoundError(f"Vacation with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Vacation]:
        """Retrieve all vacations."""
        query_stmt = select(self._vacation_table).where(
            self._vacation_table.c.vacation_collection_ref_id == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._vacation_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._vacation_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids)
            )
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Vacation:
        """Remove a vacation."""
        query_stmt = select(self._vacation_table).where(
            self._vacation_table.c.ref_id == ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise VacationNotFoundError(f"Vacation with id {ref_id} does not exist")
        remove_events(self._connection, self._vacation_event_table, ref_id)
        self._connection.execute(
            delete(self._vacation_table).where(
                self._vacation_table.c.ref_id == ref_id.as_int()
            )
        )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Vacation:
        return Vacation(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            vacation_collection_ref_id=EntityId.from_raw(
                str(row["vacation_collection_ref_id"])
            ),
            name=VacationName.from_raw(row["name"]),
            start_date=ADate.from_db(row["start_date"]),
            end_date=ADate.from_db(row["end_date"]),
        )
