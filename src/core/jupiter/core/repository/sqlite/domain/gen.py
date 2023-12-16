"""SQLite implementation of task generation infra classes."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.gen.infra.gen_log_entry_repository import (
    GenLogEntryNotFoundError,
    GenLogEntryRepository,
)
from jupiter.core.domain.gen.infra.gen_log_repository import (
    GenLogAlreadyExistsError,
    GenLogNotFoundError,
    GenLogRepository,
)
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteGenLogRepository(GenLogRepository):
    """The task generation log repository."""

    _connection: Final[AsyncConnection]
    _gen_log_table: Final[Table]
    _gen_log_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._gen_log_table = Table(
            "gen_log",
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
        self._gen_log_event_table = build_event_table(
            self._gen_log_table,
            metadata,
        )

    async def create(self, entity: GenLog) -> GenLog:
        """Create a gen log."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._gen_log_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    workspace_ref_id=entity.workspace_ref_id.as_int(),
                ),
            )
        except IntegrityError as err:
            raise GenLogAlreadyExistsError(
                f"Task generation log for workspace {entity.workspace_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._gen_log_event_table,
            entity,
        )
        return entity

    async def save(self, entity: GenLog) -> GenLog:
        """Save a task generation log."""
        result = await self._connection.execute(
            update(self._gen_log_table)
            .where(self._gen_log_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise GenLogNotFoundError("The task generation log does not exist")
        await upsert_events(
            self._connection,
            self._gen_log_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> GenLog:
        """Retrieve a task generation log."""
        query_stmt = select(self._gen_log_table).where(
            self._gen_log_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gen_log_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GenLogNotFoundError(
                f"Task generation log with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> GenLog:
        """Retrieve a gen log for a project."""
        query_stmt = select(self._gen_log_table).where(
            self._gen_log_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GenLogNotFoundError(
                f"Task generation log for user {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> GenLog:
        return GenLog(
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


class SqliteGenLogEntryRepository(GenLogEntryRepository):
    """Sqlite implementation of the task generation log entry repository."""

    _connection: Final[AsyncConnection]
    _gen_log_entry_table: Final[Table]
    _gen_log_entry_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._gen_log_entry_table = Table(
            "gen_log_entry",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "gen_log_ref_id",
                Integer,
                ForeignKey("gen_log.ref_id"),
                nullable=False,
            ),
            Column("source", String, nullable=False),
            Column("gen_even_if_not_modified", Boolean, nullable=False),
            Column("today", Date, nullable=False),
            Column("gen_targets", JSON, nullable=False),
            Column("period", JSON, nullable=True),
            Column("filter_project_ref_ids", JSON, nullable=True),
            Column("filter_habit_ref_ids", JSON, nullable=True),
            Column("filter_chore_ref_ids", JSON, nullable=True),
            Column("filter_metric_ref_ids", JSON, nullable=True),
            Column("filter_person_ref_ids", JSON, nullable=True),
            Column("filter_slack_task_ref_ids", JSON, nullable=True),
            Column("filter_email_task_ref_ids", JSON, nullable=True),
            Column("opened", Boolean, nullable=False),
            Column("entity_created_records", JSON, nullable=False),
            Column("entity_updated_records", JSON, nullable=False),
            Column("entity_removed_records", JSON, nullable=False),
            keep_existing=True,
        )
        self._gen_log_entry_event_table = build_event_table(
            self._gen_log_entry_table,
            metadata,
        )

    async def create(self, entity: GenLogEntry) -> GenLogEntry:
        """Create a task generation log entry."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._gen_log_entry_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                gen_log_ref_id=entity.gen_log_ref_id.as_int(),
                source=entity.source.value,
                gen_even_if_not_modified=entity.gen_even_if_not_modified,
                today=entity.today.to_db(),
                gen_targets=[g.value for g in entity.gen_targets],
                filter_project_ref_ids=[r.the_id for r in entity.filter_project_ref_ids]
                if entity.filter_project_ref_ids
                else None,
                filter_habit_ref_ids=[r.the_id for r in entity.filter_habit_ref_ids]
                if entity.filter_habit_ref_ids
                else None,
                filter_chore_ref_ids=[r.the_id for r in entity.filter_chore_ref_ids]
                if entity.filter_chore_ref_ids
                else None,
                filter_metric_ref_ids=[r.the_id for r in entity.filter_metric_ref_ids]
                if entity.filter_metric_ref_ids
                else None,
                filter_person_ref_ids=[r.the_id for r in entity.filter_person_ref_ids]
                if entity.filter_person_ref_ids
                else None,
                filter_slack_task_ref_ids=[
                    r.the_id for r in entity.filter_slack_task_ref_ids
                ]
                if entity.filter_slack_task_ref_ids
                else None,
                filter_email_task_ref_ids=[
                    r.the_id for r in entity.filter_email_task_ref_ids
                ]
                if entity.filter_email_task_ref_ids
                else None,
                opened=entity.opened,
                entity_created_records=[
                    r.to_json() for r in entity.entity_created_records
                ],
                entity_updated_records=[
                    r.to_json() for r in entity.entity_updated_records
                ],
                entity_removed_records=[
                    r.to_json() for r in entity.entity_removed_records
                ],
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._gen_log_entry_event_table,
            entity,
        )
        return entity

    async def save(self, entity: GenLogEntry) -> GenLogEntry:
        """Save the task generation log entry."""
        result = await self._connection.execute(
            update(self._gen_log_entry_table)
            .where(self._gen_log_entry_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                gen_log_ref_id=entity.gen_log_ref_id.as_int(),
                source=entity.source.value,
                gen_even_if_not_modified=entity.gen_even_if_not_modified,
                today=entity.today.to_db(),
                gen_targets=[g.value for g in entity.gen_targets],
                filter_project_ref_ids=[r.the_id for r in entity.filter_project_ref_ids]
                if entity.filter_project_ref_ids
                else None,
                filter_habit_ref_ids=[r.the_id for r in entity.filter_habit_ref_ids]
                if entity.filter_habit_ref_ids
                else None,
                filter_chore_ref_ids=[r.the_id for r in entity.filter_chore_ref_ids]
                if entity.filter_chore_ref_ids
                else None,
                filter_metric_ref_ids=[r.the_id for r in entity.filter_metric_ref_ids]
                if entity.filter_metric_ref_ids
                else None,
                filter_person_ref_ids=[r.the_id for r in entity.filter_person_ref_ids]
                if entity.filter_person_ref_ids
                else None,
                filter_slack_task_ref_ids=[
                    r.the_id for r in entity.filter_slack_task_ref_ids
                ]
                if entity.filter_slack_task_ref_ids
                else None,
                filter_email_task_ref_ids=[
                    r.the_id for r in entity.filter_email_task_ref_ids
                ]
                if entity.filter_email_task_ref_ids
                else None,
                opened=entity.opened,
                entity_created_records=[
                    r.to_json() for r in entity.entity_created_records
                ],
                entity_updated_records=[
                    r.to_json() for r in entity.entity_updated_records
                ],
                entity_removed_records=[
                    r.to_json() for r in entity.entity_removed_records
                ],
            ),
        )
        if result.rowcount == 0:
            raise GenLogEntryNotFoundError(
                f"The task generation log entry {entity.ref_id} does not exist"
            )
        await upsert_events(
            self._connection,
            self._gen_log_entry_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> GenLogEntry:
        """Retrieve a task generation log entry."""
        query_stmt = select(self._gen_log_entry_table).where(
            self._gen_log_entry_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gen_log_entry_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GenLogEntryNotFoundError(
                f"Task generation log entry with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[GenLogEntry]:
        """Find all task generation log entries."""
        query_stmt = select(self._gen_log_entry_table).where(
            self._gen_log_entry_table.c.gen_log_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gen_log_entry_table.c.archived.is_(False),
            )
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._gen_log_entry_table.c.ref_id.in_(
                    [ref_id.as_int() for ref_id in filter_ref_ids],
                ),
            )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def find_last(self, parent_ref_id: EntityId, limit: int) -> list[GenLogEntry]:
        """Find the last N task generation log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._gen_log_entry_table)
            .where(self._gen_log_entry_table.c.gen_log_ref_id == parent_ref_id.as_int())
            .order_by(self._gen_log_entry_table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def remove(self, ref_id: EntityId) -> GenLogEntry:
        """Remove a task generation log entry."""
        result = await self._connection.execute(
            delete(self._gen_log_entry_table).where(
                self._gen_log_entry_table.c.ref_id == ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise GenLogEntryNotFoundError(
                f"The task generation log entry {ref_id} does not exist"
            )
        await remove_events(
            self._connection,
            self._gen_log_entry_event_table,
            ref_id,
        )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> GenLogEntry:
        return GenLogEntry(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=GenLogEntry.build_name(
                [SyncTarget.from_raw(g) for g in row["gen_targets"]],
                Timestamp.from_db(row["created_time"]),
            ),
            gen_log_ref_id=EntityId.from_raw(str(row["gen_log_ref_id"])),
            source=EventSource(row["source"]),
            gen_even_if_not_modified=row["gen_even_if_not_modified"],
            today=ADate.from_db(row["today"]),
            gen_targets=[SyncTarget.from_raw(g) for g in row["gen_targets"]],
            period=[RecurringTaskPeriod.from_raw(r) for r in row["period"]]
            if row["period"]
            else None,
            filter_project_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_project_ref_ids"]
            ]
            if row["filter_project_ref_ids"]
            else None,
            filter_habit_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_habit_ref_ids"]
            ]
            if row["filter_habit_ref_ids"]
            else None,
            filter_chore_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_chore_ref_ids"]
            ]
            if row["filter_chore_ref_ids"]
            else None,
            filter_metric_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_metric_ref_ids"]
            ]
            if row["filter_metric_ref_ids"]
            else None,
            filter_person_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_person_ref_ids"]
            ]
            if row["filter_person_ref_ids"]
            else None,
            filter_slack_task_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_slack_task_ref_ids"]
            ]
            if row["filter_slack_task_ref_ids"]
            else None,
            filter_email_task_ref_ids=[
                EntityId.from_raw(r) for r in row["filter_email_task_ref_ids"]
            ]
            if row["filter_email_task_ref_ids"]
            else None,
            opened=row["opened"],
            entity_created_records=[
                EntitySummary.from_json(r) for r in row["entity_created_records"]
            ],
            entity_updated_records=[
                EntitySummary.from_json(r) for r in row["entity_updated_records"]
            ],
            entity_removed_records=[
                EntitySummary.from_json(r) for r in row["entity_removed_records"]
            ],
        )
