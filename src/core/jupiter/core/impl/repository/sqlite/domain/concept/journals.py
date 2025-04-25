"""The SQLite based journals repository."""

from typing import Final, Mapping, cast

from jupiter.core.domain.concept.journals.journal import (
    Journal,
    JournalExistsForDatePeriodCombinationError,
    JournalRepository,
)
from jupiter.core.domain.concept.journals.journal_stats import (
    JournalStats,
    JournalStatsRepository,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.realm import RealmCodecRegistry, RealmThing
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteRecordRepository,
)
from jupiter.core.impl.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteJournalRepository(SqliteLeafEntityRepository[Journal], JournalRepository):
    """A repository for journals."""

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
            already_exists_err_cls=JournalExistsForDatePeriodCombinationError,
        )

    async def find_all_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason],
        filter_periods: list[RecurringTaskPeriod],
        filter_start_date: ADate,
        filter_end_date: ADate,
    ) -> list[Journal]:
        """Find all journals in a range."""
        if len(filter_periods) == 0:
            return []

        query_stmt = self._table.select().where(
            self._table.c.journal_collection_ref_id == parent_ref_id.as_int(),
        )

        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )

        query_stmt = query_stmt.where(
            self._table.c.period.in_([p.value for p in filter_periods])
        )
        query_stmt = query_stmt.where(
            self._table.c.right_now >= filter_start_date.the_date
        )
        query_stmt = query_stmt.where(
            self._table.c.right_now <= filter_end_date.the_date
        )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]


class SqliteJournalStatsRepository(
    SqliteRecordRepository[JournalStats, EntityId], JournalStatsRepository
):
    """The journal stats repository."""

    _journal_stats_table: Final[Table]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, connection, metadata)
        self._journal_stats_table = Table(
            "journal_stats",
            metadata,
            Column(
                "journal_ref_id",
                Integer,
                ForeignKey("journal.ref_id"),
                nullable=False,
            ),
            Column("report", JSON, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: JournalStats) -> JournalStats:
        """Create a new journal stats."""
        try:
            await self._connection.execute(
                insert(self._journal_stats_table).values(
                    **(
                        cast(
                            Mapping[str, RealmThing],
                            self._realm_codec_registry.db_encode(record),
                        )
                    ),
                ),
            )
        except IntegrityError as err:
            raise RecordAlreadyExistsError(
                f"Journal stats for journal {record.journal.ref_id} already exists",
            ) from err
        return record

    async def save(self, record: JournalStats) -> JournalStats:
        """Save a journal stats."""
        result = await self._connection.execute(
            update(self._journal_stats_table)
            .where(
                self._journal_stats_table.c.journal_ref_id == record.journal.as_int()
            )
            .values(
                **(
                    cast(
                        Mapping[str, RealmThing],
                        self._realm_codec_registry.db_encode(record),
                    )
                )
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The journal stats {record.journal.ref_id} does not exist"
            )
        return record

    async def remove(self, key: EntityId) -> None:
        """Remove a journal stats."""
        result = await self._connection.execute(
            delete(self._journal_stats_table).where(
                self._journal_stats_table.c.journal_ref_id == key.as_int()
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The journal stats for journal {key} does not exist"
            )

    async def load_by_key_optional(self, key: EntityId) -> JournalStats | None:
        """Load a journal stats by it's unique key."""
        result = await self._connection.execute(
            select(self._journal_stats_table).where(
                self._journal_stats_table.c.journal_ref_id == key.as_int()
            )
        )
        result_x = result.first()
        if result_x is None:
            return None
        return self._row_to_entity(result_x)

    async def find_all(self, prefix: EntityId | list[EntityId]) -> list[JournalStats]:
        """Find all journal stats for a journal."""
        result = await self._connection.execute(
            select(self._journal_stats_table).where(
                self._journal_stats_table.c.journal_ref_id.in_(
                    [prefix.as_int()]
                    if isinstance(prefix, EntityId)
                    else [p.as_int() for p in prefix]
                )
            )
        )
        results = result.fetchall()
        return [self._row_to_entity(row) for row in results]

    def _row_to_entity(self, row: RowType) -> JournalStats:
        return self._realm_codec_registry.db_decode(
            JournalStats, cast(Mapping[str, RealmThing], row._mapping)
        )
