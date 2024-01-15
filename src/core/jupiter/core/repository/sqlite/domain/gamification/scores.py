"""SQLite implementation of gamification task scores classes."""
from typing import Final, List, Tuple

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.gamification.infra.score_log_entry_repository import (
    ScoreLogEntryRepository,
)
from jupiter.core.domain.gamification.infra.score_log_repository import (
    ScoreLogRepository,
)
from jupiter.core.domain.gamification.infra.score_period_best_repository import (
    ScorePeriodBestRepository,
)
from jupiter.core.domain.gamification.infra.score_stats_repository import (
    ScoreStatsRepository,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gamification.score_period_best import ScorePeriodBest
from jupiter.core.domain.gamification.score_source import ScoreSource
from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
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


class SqliteScoreLogRepository(
    SqliteTrunkEntityRepository[ScoreLog], ScoreLogRepository
):
    """The score log repository."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            Table(
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
            ),
        )

    def _entity_to_row(self, entity: ScoreLog) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "user_ref_id": entity.user.as_int(),
        }

    def _row_to_entity(self, row: RowType) -> ScoreLog:
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
            user=ParentLink(EntityId.from_raw(str(row["user_ref_id"]))),
        )


class SqliteScoreLogEntryRepository(
    SqliteLeafEntityRepository[ScoreLogEntry], ScoreLogEntryRepository
):
    """Sqlite implementation of the score log entry repository."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            Table(
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
                Column("has_lucky_puppy_bonus", Boolean, nullable=True),
                Column("success", Boolean, nullable=False),
                Column("score", Integer, nullable=False),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: ScoreLogEntry) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "score_log_ref_id": entity.score_log.as_int(),
            "source": entity.source.value,
            "task_ref_id": entity.task_ref_id.as_int(),
            "difficulty": entity.difficulty.value if entity.difficulty else None,
            "success": entity.success,
            "has_lucky_puppy_bonus": entity.has_lucky_puppy_bonus,
            "score": entity.score,
        }

    def _row_to_entity(self, row: RowType) -> ScoreLogEntry:
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
            score_log=ParentLink(EntityId.from_raw(str(row["score_log_ref_id"]))),
            source=ScoreSource(row["source"]),
            task_ref_id=EntityId.from_raw(str(row["task_ref_id"])),
            difficulty=Difficulty(row["difficulty"]) if row["difficulty"] else None,
            success=row["success"],
            has_lucky_puppy_bonus=row["has_lucky_puppy_bonus"],
            score=row["score"],
        )


class SqliteScoreStatsRepository(ScoreStatsRepository):
    """Sqlite implementation of the score stats repository."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _connection: Final[AsyncConnection]
    _score_stats_table: Final[Table]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
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
            Column("inbox_task_cnt", Integer, nullable=False),
            Column("big_plan_cnt", Integer, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: ScoreStats) -> ScoreStats:
        """Create a score stats."""
        try:
            await self._connection.execute(
                insert(self._score_stats_table).values(
                    created_time=record.created_time.to_db(),
                    last_modified_time=record.last_modified_time.to_db(),
                    score_log_ref_id=record.score_log.as_int(),
                    period=record.period.value if record.period else None,
                    timeline=record.timeline,
                    total_score=record.total_score,
                    inbox_task_cnt=record.inbox_task_cnt,
                    big_plan_cnt=record.big_plan_cnt,
                ),
            )
        except IntegrityError as err:
            raise RecordAlreadyExistsError(
                f"Score stats for score log {record.score_log.ref_id}:{record.period}:{record.timeline} already exists",
            ) from err
        return record

    async def save(self, record: ScoreStats) -> ScoreStats:
        """Save a score stats."""
        result = await self._connection.execute(
            update(self._score_stats_table)
            .where(
                self._score_stats_table.c.score_log_ref_id == record.score_log.as_int()
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
                inbox_task_cnt=record.inbox_task_cnt,
                big_plan_cnt=record.big_plan_cnt,
            ),
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The score stats {record.score_log.ref_id}:{record.period}:{record.timeline} does not exist"
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
            raise RecordNotFoundError(
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
            raise RecordNotFoundError(
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

    async def find_all_in_timerange(
        self,
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod,
        start_date: ADate,
        end_date: ADate,
    ) -> list[ScoreStats]:
        """Find all score stats in a given time range."""
        result = await self._connection.execute(
            select(self._score_stats_table)
            .where(
                self._score_stats_table.c.score_log_ref_id == score_log_ref_id.as_int()
            )
            .where(self._score_stats_table.c.period == period.value)
            .where(self._score_stats_table.c.created_time >= start_date.to_db())
            .where(
                self._score_stats_table.c.created_time
                <= end_date.to_timestamp_at_end_of_day().to_db()
            )
        )

        return [self._row_to_entity(row) for row in result]

    def _row_to_entity(self, row: RowType) -> ScoreStats:
        return ScoreStats(
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            score_log=ParentLink(EntityId.from_raw(str(row["score_log_ref_id"]))),
            period=RecurringTaskPeriod(row["period"]) if row["period"] else None,
            timeline=row["timeline"],
            total_score=row["total_score"],
            inbox_task_cnt=row["inbox_task_cnt"],
            big_plan_cnt=row["big_plan_cnt"],
        )


class SqliteScorePeriodBestRepository(ScorePeriodBestRepository):
    """Sqlite implementation of the score period best repository."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _connection: Final[AsyncConnection]
    _score_period_best_table: Final[Table]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._connection = connection
        self._score_period_best_table = Table(
            "gamification_score_period_best",
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
            Column("sub_period", String, nullable=False),
            Column("total_score", Integer, nullable=False),
            Column("inbox_task_cnt", Integer, nullable=False),
            Column("big_plan_cnt", Integer, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: ScorePeriodBest) -> ScorePeriodBest:
        """Create a score period best."""
        try:
            await self._connection.execute(
                insert(self._score_period_best_table).values(
                    created_time=record.created_time.to_db(),
                    last_modified_time=record.last_modified_time.to_db(),
                    score_log_ref_id=record.score_log.as_int(),
                    period=record.period.value if record.period else None,
                    timeline=record.timeline,
                    sub_period=record.sub_period.value,
                    total_score=record.total_score,
                    inbox_task_cnt=record.inbox_task_cnt,
                    big_plan_cnt=record.big_plan_cnt,
                ),
            )
        except IntegrityError as err:
            raise RecordAlreadyExistsError(
                f"Score period best for score log {record.score_log}:{record.period}:{record.timeline}:{record.sub_period} already exists",
            ) from err
        return record

    async def save(self, record: ScorePeriodBest) -> ScorePeriodBest:
        """Save a score period best."""
        result = await self._connection.execute(
            update(self._score_period_best_table)
            .where(
                self._score_period_best_table.c.score_log_ref_id
                == record.score_log.as_int()
            )
            .where(
                self._score_period_best_table.c.period == record.period.value
                if record.period is not None
                else self._score_period_best_table.c.period.is_(None)
            )
            .where(self._score_period_best_table.c.timeline == record.timeline)
            .where(
                self._score_period_best_table.c.sub_period == record.sub_period.value
            )
            .values(
                created_time=record.created_time.to_db(),
                last_modified_time=record.last_modified_time.to_db(),
                total_score=record.total_score,
                inbox_task_cnt=record.inbox_task_cnt,
                big_plan_cnt=record.big_plan_cnt,
            ),
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The score period best {record.score_log}:{record.period}:{record.timeline}:{record.sub_period} does not exist"
            )
        return record

    async def remove(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod]
    ) -> ScorePeriodBest:
        """Remove a score period best."""
        result = await self._connection.execute(
            delete(self._score_period_best_table)
            .where(self._score_period_best_table.c.score_log_ref_id == key[0].as_int())
            .where(
                self._score_period_best_table.c.period == key[1].value
                if key[1] is not None
                else self._score_period_best_table.c.period.is_(None)
            )
            .where(self._score_period_best_table.c.timeline == key[2])
            .where(self._score_period_best_table.c.sub_period == key[3].value)
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The score period best {key[0]}:{key[1]}:{key[2]}:{key[3]} does not exist"
            )
        return self._row_to_entity(result)

    async def load_by_key(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod]
    ) -> ScorePeriodBest:
        """Load a score period best by its unique key."""
        result = (
            await self._connection.execute(
                select(self._score_period_best_table)
                .where(
                    self._score_period_best_table.c.score_log_ref_id == key[0].as_int()
                )
                .where(
                    self._score_period_best_table.c.period == key[1].value
                    if key[1] is not None
                    else self._score_period_best_table.c.period.is_(None)
                )
                .where(self._score_period_best_table.c.timeline == key[2])
                .where(self._score_period_best_table.c.sub_period == key[3].value)
            )
        ).first()
        if result is None:
            raise RecordNotFoundError(
                f"Score period best {key[0]}:{key[1]}:{key[2]}:{key[3]} does not exist"
            )
        return self._row_to_entity(result)

    async def load_by_key_optional(
        self, key: Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod]
    ) -> ScorePeriodBest | None:
        """Load a score period best by it's unique key."""
        result = (
            await self._connection.execute(
                select(self._score_period_best_table)
                .where(
                    self._score_period_best_table.c.score_log_ref_id == key[0].as_int()
                )
                .where(
                    self._score_period_best_table.c.period == key[1].value
                    if key[1] is not None
                    else self._score_period_best_table.c.period.is_(None)
                )
                .where(self._score_period_best_table.c.timeline == key[2])
                .where(self._score_period_best_table.c.sub_period == key[3].value)
            )
        ).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def find_all(self, prefix: EntityId) -> List[ScorePeriodBest]:
        """Find all score period best for a score log."""
        result = await self._connection.execute(
            select(self._score_period_best_table).where(
                self._score_period_best_table.c.score_log_ref_id == prefix.as_int()
            )
        )
        return [self._row_to_entity(row) for row in result]

    def _row_to_entity(self, row: RowType) -> ScorePeriodBest:
        return ScorePeriodBest(
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            score_log=ParentLink(EntityId.from_raw(str(row["score_log_ref_id"]))),
            period=RecurringTaskPeriod(row["period"]) if row["period"] else None,
            timeline=row["timeline"],
            sub_period=RecurringTaskPeriod(row["sub_period"]),
            total_score=row["total_score"],
            inbox_task_cnt=row["inbox_task_cnt"],
            big_plan_cnt=row["big_plan_cnt"],
        )
