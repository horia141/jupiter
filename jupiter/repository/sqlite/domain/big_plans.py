"""The SQLite big plans repository."""
import uuid
from typing import Optional, Iterable, Final

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, ForeignKey, update, select,\
    delete, Unicode, String
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository, \
    BigPlanCollectionNotFoundError
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository, BigPlanNotFoundError
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import upsert_events, build_event_table, remove_events


class SqliteBigPlanCollectionRepository(BigPlanCollectionRepository):
    """The big plan collection repository."""

    _connection: Final[Connection]
    _big_plan_collection_table: Final[Table]
    _big_plan_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._big_plan_collection_table = Table(
            'big_plan_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('project_ref_id', Integer, ForeignKey("project.ref_id"), unique=True, nullable=False),
            keep_existing=True)
        self._big_plan_collection_event_table = build_event_table(self._big_plan_collection_table, metadata)

    def create(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Create a big plan collection."""
        result = self._connection.execute(
            insert(self._big_plan_collection_table).values(
                ref_id=big_plan_collection.ref_id.as_int() if big_plan_collection.ref_id != BAD_REF_ID else None,
                version=big_plan_collection.version,
                archived=big_plan_collection.archived,
                created_time=big_plan_collection.created_time.to_db(),
                last_modified_time=big_plan_collection.last_modified_time.to_db(),
                archived_time=big_plan_collection.archived_time.to_db() if big_plan_collection.archived_time else None,
                project_ref_id=big_plan_collection.project_ref_id.as_int()))
        big_plan_collection = big_plan_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._big_plan_collection_event_table, big_plan_collection)
        return big_plan_collection

    def save(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Save a big big plan collection."""
        result = self._connection.execute(
            update(self._big_plan_collection_table)
            .where(self._big_plan_collection_table.c.ref_id == big_plan_collection.ref_id.as_int())
            .values(
                version=big_plan_collection.version,
                archived=big_plan_collection.archived,
                created_time=big_plan_collection.created_time.to_db(),
                last_modified_time=big_plan_collection.last_modified_time.to_db(),
                archived_time=big_plan_collection.archived_time.to_db() if big_plan_collection.archived_time else None,
                project_ref_id=big_plan_collection.project_ref_id.as_int()))
        if result.rowcount == 0:
            raise BigPlanCollectionNotFoundError("The big plan collection does not exist")
        upsert_events(self._connection, self._big_plan_collection_event_table, big_plan_collection)
        return big_plan_collection

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlanCollection:
        """Load a big plan collection."""
        query_stmt = \
            select(self._big_plan_collection_table)\
                .where(self._big_plan_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._big_plan_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise BigPlanCollectionNotFoundError(f"Big plan collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_project(self, project_ref_id: EntityId) -> BigPlanCollection:
        """Load a big plan collection for a given project."""
        query_stmt = \
            select(self._big_plan_collection_table)\
                .where(self._big_plan_collection_table.c.project_ref_id == project_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise BigPlanCollectionNotFoundError(f"Big plan collection for project {project_ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlanCollection]:
        """Retrieve all big plan collections."""
        query_stmt = select(self._big_plan_collection_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._big_plan_collection_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = \
                query_stmt.where(self._big_plan_collection_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_project_ref_ids:
            query_stmt = query_stmt.where(
                self._big_plan_collection_table.c.project_ref_id.in_(fi.as_int() for fi in filter_project_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> BigPlanCollection:
        """Remove a big plan collection."""
        query_stmt = \
            select(self._big_plan_collection_table)\
                .where(self._big_plan_collection_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise BigPlanCollectionNotFoundError(f"big plan collection with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._big_plan_collection_table).where(self._big_plan_collection_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._big_plan_collection_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> BigPlanCollection:
        return BigPlanCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])))


class SqliteBigPlanRepository(BigPlanRepository):
    """The big plan repository."""

    _connection: Final[Connection]
    _big_plan_table: Final[Table]
    _big_plan_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._big_plan_table = Table(
            'big_plan',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('big_plan_collection_ref_id', Integer, ForeignKey("big_plan_collection.ref_id"), nullable=False),
            Column('name', Unicode(), nullable=False),
            Column('status', String(16), nullable=False),
            Column('actionable_date', DateTime, nullable=True),
            Column('due_date', DateTime, nullable=True),
            Column('notion_link_uuid', String(16), nullable=False),
            Column('accepted_time', DateTime, nullable=True),
            Column('working_time', DateTime, nullable=True),
            Column('completed_time', DateTime, nullable=True),
            keep_existing=True)
        self._big_plan_event_table = build_event_table(self._big_plan_table, metadata)

    def create(self, big_plan: BigPlan) -> BigPlan:
        """Create the big plan."""
        result = self._connection.execute(
            insert(self._big_plan_table) \
                .values(
                    ref_id=big_plan.ref_id.as_int() if big_plan.ref_id != BAD_REF_ID else None,
                    version=big_plan.version,
                    archived=big_plan.archived,
                    created_time=big_plan.created_time.to_db(),
                    last_modified_time=big_plan.last_modified_time.to_db(),
                    archived_time=big_plan.archived_time.to_db() if big_plan.archived_time else None,
                    big_plan_collection_ref_id=big_plan.big_plan_collection_ref_id.as_int(),
                    name=str(big_plan.name),
                    status=str(big_plan.status),
                    actionable_date=big_plan.actionable_date.to_db() if big_plan.actionable_date else None,
                    due_date=big_plan.due_date.to_db() if big_plan.due_date else None,
                    notion_link_uuid=str(big_plan.notion_link_uuid),
                    accepted_time=big_plan.accepted_time.to_db() if big_plan.accepted_time else None,
                    working_time=big_plan.working_time.to_db() if big_plan.working_time else None,
                    completed_time=big_plan.completed_time.to_db() if big_plan.completed_time else None))
        big_plan = big_plan.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._big_plan_event_table, big_plan)
        return big_plan

    def save(self, big_plan: BigPlan) -> BigPlan:
        """Save the big plan."""
        result = self._connection.execute(
            update(self._big_plan_table)
            .where(self._big_plan_table.c.ref_id == big_plan.ref_id.as_int())
            .values(
                ref_id=big_plan.ref_id.as_int() if big_plan.ref_id != BAD_REF_ID else None,
                version=big_plan.version,
                archived=big_plan.archived,
                created_time=big_plan.created_time.to_db(),
                last_modified_time=big_plan.last_modified_time.to_db(),
                archived_time=big_plan.archived_time.to_db() if big_plan.archived_time else None,
                big_plan_collection_ref_id=big_plan.big_plan_collection_ref_id.as_int(),
                name=str(big_plan.name),
                status=str(big_plan.status),
                actionable_date=big_plan.actionable_date.to_db() if big_plan.actionable_date else None,
                due_date=big_plan.due_date.to_db() if big_plan.due_date else None,
                notion_link_uuid=str(big_plan.notion_link_uuid),
                accepted_time=big_plan.accepted_time.to_db() if big_plan.accepted_time else None,
                working_time=big_plan.working_time.to_db() if big_plan.working_time else None,
                completed_time=big_plan.completed_time.to_db() if big_plan.completed_time else None))
        if result.rowcount == 0:
            raise BigPlanNotFoundError(f"Big plan with id {big_plan.ref_id} does not exist")
        upsert_events(self._connection, self._big_plan_event_table, big_plan)
        return big_plan

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlan:
        """Retrieve the big plan."""
        query_stmt = select(self._big_plan_table).where(self._big_plan_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._big_plan_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise BigPlanNotFoundError(f"Big plan with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_collection_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Find all the big plans."""
        query_stmt = select(self._big_plan_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._big_plan_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._big_plan_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_big_plan_collection_ref_ids:
            query_stmt = query_stmt.where(
                self._big_plan_table.c.big_plan_collection_ref_id.in_(
                    fi.as_int() for fi in filter_big_plan_collection_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> BigPlan:
        """Remove a bit plan."""
        query_stmt = select(self._big_plan_table).where(self._big_plan_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise BigPlanNotFoundError(f"Big plan with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._big_plan_table).where(self._big_plan_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._big_plan_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> BigPlan:
        return BigPlan(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            big_plan_collection_ref_id=EntityId.from_raw(str(row["big_plan_collection_ref_id"])),
            name=BigPlanName.from_raw(row["name"]),
            status=BigPlanStatus.from_raw(row["status"]),
            actionable_date=ADate.from_db(row["actionable_date"]) if row["actionable_date"] else None,
            due_date=ADate.from_db(row["due_date"]) if row["due_date"] else None,
            notion_link_uuid=uuid.UUID(row["notion_link_uuid"]),
            accepted_time=Timestamp.from_db(row["accepted_time"]) if row["accepted_time"] else None,
            working_time=Timestamp.from_db(row["working_time"]) if row["working_time"] else None,
            completed_time=Timestamp.from_db(row["completed_time"]) if row["completed_time"] else None)
