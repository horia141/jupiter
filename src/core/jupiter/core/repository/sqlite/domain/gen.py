"""SQLite implementation of task generation infra classes."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.gen.infra.gen_log_entry_repository import (
    GenLogEntryRepository,
)
from jupiter.core.domain.gen.infra.gen_log_repository import (
    GenLogRepository,
)
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
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
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteGenLogRepository(SqliteTrunkEntityRepository[GenLog], GenLogRepository):
    """The task generation log repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    @staticmethod
    def _entity_to_row(entity: GenLog) -> RowType:
        return {
            "ref_id": entity.ref_id.as_int(),
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace_ref_id.as_int(),
        }

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

    @staticmethod
    def _get_parent_field_name() -> str:
        return "workspace_ref_id"


class SqliteGenLogEntryRepository(
    SqliteLeafEntityRepository[GenLogEntry], GenLogEntryRepository
):
    """Sqlite implementation of the task generation log entry repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    async def find_last(self, parent_ref_id: EntityId, limit: int) -> list[GenLogEntry]:
        """Find the last N task generation log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._table)
            .where(self._table.c.gen_log_ref_id == parent_ref_id.as_int())
            .order_by(self._table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    @staticmethod
    def _entity_to_row(entity: GenLogEntry) -> RowType:
        return {
            "ref_id": entity.ref_id.as_int(),
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "gen_log_ref_id": entity.gen_log_ref_id.as_int(),
            "source": entity.source.value,
            "gen_even_if_not_modified": entity.gen_even_if_not_modified,
            "today": entity.today.to_db(),
            "gen_targets": [g.value for g in entity.gen_targets],
            "period": [p.value for p in entity.period] if entity.period else None,
            "filter_project_ref_ids": [r.the_id for r in entity.filter_project_ref_ids]
            if entity.filter_project_ref_ids
            else None,
            "filter_habit_ref_ids": [r.the_id for r in entity.filter_habit_ref_ids]
            if entity.filter_habit_ref_ids
            else None,
            "filter_chore_ref_ids": [r.the_id for r in entity.filter_chore_ref_ids]
            if entity.filter_chore_ref_ids
            else None,
            "filter_metric_ref_ids": [r.the_id for r in entity.filter_metric_ref_ids]
            if entity.filter_metric_ref_ids
            else None,
            "filter_person_ref_ids": [r.the_id for r in entity.filter_person_ref_ids]
            if entity.filter_person_ref_ids
            else None,
            "filter_slack_task_ref_ids": [
                r.the_id for r in entity.filter_slack_task_ref_ids
            ]
            if entity.filter_slack_task_ref_ids
            else None,
            "filter_email_task_ref_ids": [
                r.the_id for r in entity.filter_email_task_ref_ids
            ]
            if entity.filter_email_task_ref_ids
            else None,
            "opened": entity.opened,
            "entity_created_records": [
                r.to_json() for r in entity.entity_created_records
            ],
            "entity_updated_records": [
                r.to_json() for r in entity.entity_updated_records
            ],
            "entity_removed_records": [
                r.to_json() for r in entity.entity_removed_records
            ],
        }

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

    @staticmethod
    def _get_parent_field_name() -> str:
        return "gen_log_ref_id"
