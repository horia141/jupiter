"""SQLite implementation of gamification task scores classes."""
from typing import Final, Iterable, List, Optional, Tuple

from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.gamification.infra.score_log_entry_repository import (
    ScoreLogEntryAlreadyExistsError,
    ScoreLogEntryNotFoundError,
    ScoreLogEntryRepository,
)
from jupiter.core.domain.gamification.infra.score_log_repository import (
    ScoreLogAlreadyExistsError,
    ScoreLogNotFoundError,
    ScoreLogRepository,
)
from jupiter.core.domain.gamification.infra.score_stats_repository import (
    ScoreStatsRepository,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gamification.score_source import ScoureSource
from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
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


class SqliteScoreLogRepository(ScoreLogRepository):
    """The score log repository."""

    _connection: Final[AsyncConnection]
    _score_log_table: Final[Table]
    _score_log_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._score_log_table = Table(
            "gamification_score_log",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "user_ref_id",
                Integer,
                ForeignKey("user.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            keep_existing=True,
        )
        self._score_log_event_table = build_event_table(
            self._score_log_table,
            metadata,
        )

    async def create(self, entity: ScoreLog) -> ScoreLog:
        """Create a score log."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._score_log_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    user_ref_id=entity.user_ref_id.as_int(),
                ),
            )
        except IntegrityError as err:
            raise ScoreLogAlreadyExistsError(
                f"Score log for user {entity.user_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._score_log_event_table,
            entity,
        )
        return entity

    async def save(self, entity: ScoreLog) -> ScoreLog:
        """Save a score log."""
        result = await self._connection.execute(
            update(self._score_log_table)
            .where(self._score_log_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                user_ref_id=entity.user_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise ScoreLogNotFoundError("The score log does not exist")
        await upsert_events(
            self._connection,
            self._score_log_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> ScoreLog:
        """Retrieve a score log."""
        query_stmt = select(self._score_log_table).where(
            self._score_log_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._score_log_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ScoreLogNotFoundError(
                f"Score log with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> ScoreLog:
        """Retrieve a score log for a project."""
        query_stmt = select(self._score_log_table).where(
            self._score_log_table.c.user_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ScoreLogNotFoundError(
                f"Score log for user {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> ScoreLog:
        return ScoreLog(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            user_ref_id=EntityId.from_raw(str(row["user_ref_id"])),
        )


class SqliteScoreLogEntryRepository(ScoreLogEntryRepository):
    """Sqlite implementation of the score log entry repository."""

    _connection: Final[AsyncConnection]
    _score_log_entry_table: Final[Table]
    _score_log_entry_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._score_log_entry_table = Table(
            "gamification_score_log_entry",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "score_log_ref_id",
                Integer,
                ForeignKey("gamification_score_log.ref_id"),
                nullable=False,
            ),
            Column("source", String, nullable=False),
            Column("task_ref_id", Integer, nullable=False),
            Column("difficulty", String, nullable=True),
            Column("success", Boolean, nullable=False),
            Column("score", Integer, nullable=False),
            keep_existing=True,
        )
        self._score_log_entry_event_table = build_event_table(
            self._score_log_entry_table,
            metadata,
        )

    async def create(self, entity: ScoreLogEntry) -> ScoreLogEntry:
        """Create a score log entry."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._score_log_entry_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    score_log_ref_id=entity.score_log_ref_id.as_int(),
                    source=entity.source.value,
                    task_ref_id=entity.task_ref_id.as_int(),
                    difficulty=entity.difficulty.value if entity.difficulty else None,
                    success=entity.success,
                    score=entity.score,
                ),
            )
        except IntegrityError as err:
            raise ScoreLogEntryAlreadyExistsError(
                f"Score log entry for score log {entity.score_log_ref_id}:{entity.source}:{entity.task_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._score_log_entry_event_table,
            entity,
        )
        return entity

    async def save(self, entity: ScoreLogEntry) -> ScoreLogEntry:
        """Save the score log entry."""
        result = await self._connection.execute(
            update(self._score_log_entry_table)
            .where(self._score_log_entry_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                score_log_ref_id=entity.score_log_ref_id.as_int(),
                source=entity.source.value,
                task_ref_id=entity.task_ref_id.as_int(),
                difficulty=entity.difficulty.value if entity.difficulty else None,
                success=entity.success,
                score=entity.score,
            ),
        )
        if result.rowcount == 0:
            raise ScoreLogEntryNotFoundError(
                f"The score log entry {entity.ref_id} does not exist"
            )
        await upsert_events(
            self._connection,
            self._score_log_entry_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> ScoreLogEntry:
        """Retrieve a score log entry."""
        query_stmt = select(self._score_log_entry_table).where(
            self._score_log_entry_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._score_log_entry_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ScoreLogEntryNotFoundError(
                f"Score log entry with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[ScoreLogEntry]:
        """Find all score log entries."""
        query_stmt = select(self._score_log_entry_table).where(
            self._score_log_entry_table.c.score_log_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._score_log_entry_table.c.archived.is_(False),
            )
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._score_log_entry_table.c.ref_id.in_(
                    [ref_id.as_int() for ref_id in filter_ref_ids],
                ),
            )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def remove(self, ref_id: EntityId) -> ScoreLogEntry:
        """Remove a score log entry."""
        result = await self._connection.execute(
            delete(self._score_log_entry_table).where(
                self._score_log_entry_table.c.ref_id == ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise ScoreLogEntryNotFoundError(
                f"The score log entry {ref_id} does not exist"
            )
        await remove_events(
            self._connection,
            self._score_log_entry_event_table,
            ref_id,
        )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> ScoreLogEntry:
        return ScoreLogEntry(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=EntityName(row["name"]),
            score_log_ref_id=EntityId.from_raw(str(row["score_log_ref_id"])),
            source=ScoureSource(row["source"]),
            task_ref_id=EntityId.from_raw(str(row["task_ref_id"])),
            difficulty=Difficulty(row["difficulty"]) if row["difficulty"] else None,
            success=row["success"],
            score=row["score"],
        )


class SqliteScoreStatsRepository(ScoreStatsRepository):
    """Sqlite implementation of the score stats repository."""

    _connection: Final[AsyncConnection]
    _score_stats_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._score_stats_table = Table(
            "gamification_score_stats",
            metadata,
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column(
                "score_log_ref_id",
                Integer,
                ForeignKey("gamification_score_log.ref_id"),
                nullable=False,
            ),
            Column("period", String, nullable=True),
            Column("timeline", String, nullable=False),
            Column("total_score", Integer, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: ScoreStats) -> ScoreStats:
        """Create a score stats."""
        try:
            await self._connection.execute(
                insert(self._score_stats_table).values(
                    created_time=record.created_time.to_db(),
                    last_modified_time=record.last_modified_time.to_db(),
                    score_log_ref_id=record.score_log_ref_id.as_int(),
                    period=record.period.value if record.period else None,
                    timeline=record.timeline,
                    total_score=record.total_score,
                ),
            )
        except IntegrityError as err:
            raise ScoreLogAlreadyExistsError(
                f"Score stats for score log {record.score_log_ref_id}:{record.period}:{record.timeline} already exists",
            ) from err
        return record

    async def save(self, record: ScoreStats) -> ScoreStats:
        """Save a score stats."""
        result = await self._connection.execute(
            update(self._score_stats_table)
            .where(
                self._score_stats_table.c.score_log_ref_id
                == record.score_log_ref_id.as_int()
            )
            .where(
                self._score_stats_table.c.period == record.period.value
                if record.period is not None
                else self._score_stats_table.c.period.is_(None)
            )
            .where(self._score_stats_table.c.timeline == record.timeline)
            .values(
                created_time=record.created_time.to_db(),
                last_modified_time=record.last_modified_time.to_db(),
                total_score=record.total_score,
            ),
        )
        if result.rowcount == 0:
            raise ScoreLogNotFoundError(
                f"The score stats {record.score_log_ref_id}:{record.period}:{record.timeline} does not exist"
            )
        return record

    async def remove(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str]
    ) -> ScoreStats:
        """Remove a score stats."""
        result = await self._connection.execute(
            delete(self._score_stats_table)
            .where(self._score_stats_table.c.score_log_ref_id == key[0].as_int())
            .where(
                self._score_stats_table.c.period == key[1].value
                if key[1] is not None
                else self._score_stats_table.c.period.is_(None)
            )
            .where(self._score_stats_table.c.timeline == key[2])
        )
        if result.rowcount == 0:
            raise ScoreLogNotFoundError(
                f"The score stats {key[0]}:{key[1]}:{key[2]} does not exist"
            )
        return self._row_to_entity(result)

    async def load_by_key(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str]
    ) -> ScoreStats:
        """Load a score stats by it's unique key."""
        result = (
            await self._connection.execute(
                select(self._score_stats_table)
                .where(self._score_stats_table.c.score_log_ref_id == key[0].as_int())
                .where(
                    self._score_stats_table.c.period == key[1].value
                    if key[1] is not None
                    else self._score_stats_table.c.period.is_(None)
                )
                .where(self._score_stats_table.c.timeline == key[2])
            )
        ).first()
        if result is None:
            raise ScoreLogNotFoundError(
                f"Score stats {key[0]}:{key[1]}:{key[2]} does not exist"
            )
        return self._row_to_entity(result)

    async def load_by_key_optional(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str]
    ) -> ScoreStats | None:
        """Load a score stats by it's unique key."""
        result = (
            await self._connection.execute(
                select(self._score_stats_table)
                .where(self._score_stats_table.c.score_log_ref_id == key[0].as_int())
                .where(
                    self._score_stats_table.c.period == key[1].value
                    if key[1] is not None
                    else self._score_stats_table.c.period.is_(None)
                )
                .where(self._score_stats_table.c.timeline == key[2])
            )
        ).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def find_all(self, prefix: EntityId) -> List[ScoreStats]:
        """Find all score stats for a score log."""
        result = await self._connection.execute(
            select(self._score_stats_table).where(
                self._score_stats_table.c.score_log_ref_id == prefix.as_int()
            )
        )
        return [self._row_to_entity(row) for row in result]

    def _row_to_entity(self, row: RowType) -> ScoreStats:
        return ScoreStats(
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            score_log_ref_id=EntityId.from_raw(str(row["score_log_ref_id"])),
            period=RecurringTaskPeriod(row["period"]) if row["period"] else None,
            timeline=row["timeline"],
            total_score=row["total_score"],
        )