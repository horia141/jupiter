"""The SQLite repository for habits."""

from sqlite3 import IntegrityError
from typing import Final, Mapping, cast

from jupiter.core.domain.concept.habits.habit_streak_mark import (
    HabitStreakMark,
    HabitStreakMarkRepository,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.realm import RealmCodecRegistry, RealmThing
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from jupiter.core.impl.repository.sqlite.infra.repository import SqliteRecordRepository
from jupiter.core.impl.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Column,
    Date,
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
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteHabitStreakMarkRepository(
    SqliteRecordRepository[HabitStreakMark, tuple[EntityId, int, ADate]],
    HabitStreakMarkRepository,
):
    """The SQLite repository for habit streak marks."""

    _habit_streak_mark_table: Final[Table]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, connection, metadata)
        self._habit_streak_mark_table = Table(
            "habit_streak_marks",
            metadata,
            Column("habit_ref_id", Integer, ForeignKey("habit.ref_id"), nullable=False),
            Column("date", Date, nullable=False),
            Column("statuses", JSON, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: HabitStreakMark) -> HabitStreakMark:
        """Create a new habit streak mark."""
        try:
            await self._connection.execute(
                insert(self._habit_streak_mark_table).values(
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
                f"Habit streak mark for habit {record.habit.ref_id} already exists",
            ) from err
        return record

    async def save(self, record: HabitStreakMark) -> HabitStreakMark:
        """Save a habit streak mark."""
        result = await self._connection.execute(
            update(self._habit_streak_mark_table)
            .where(
                self._habit_streak_mark_table.c.habit_ref_id == record.habit.as_int()
            )
            .where(
                self._habit_streak_mark_table.c.date
                == self._realm_codec_registry.db_encode(record.date)
            )
            .values(
                **(
                    cast(
                        Mapping[str, RealmThing],
                        self._realm_codec_registry.db_encode(record),
                    )
                ),
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"Habit streak mark for habit {record.habit.ref_id} already exists",
            )
        return record

    async def remove(self, key: tuple[EntityId, ADate]) -> None:
        """Remove a habit streak mark."""
        result = await self._connection.execute(
            delete(self._habit_streak_mark_table)
            .where(self._habit_streak_mark_table.c.habit_ref_id == key[0].as_int())
            .where(
                self._habit_streak_mark_table.c.date
                == self._realm_codec_registry.db_encode(key[1])
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"Habit streak mark for habit {key[0]} already exists",
            )

    async def load_by_key_optional(
        self, key: tuple[EntityId, ADate]
    ) -> HabitStreakMark | None:
        """Load a habit streak mark by it's unique key."""
        result = await self._connection.execute(
            select(self._habit_streak_mark_table)
            .where(self._habit_streak_mark_table.c.habit_ref_id == key[0].as_int())
            .where(
                self._habit_streak_mark_table.c.date
                == self._realm_codec_registry.db_encode(key[1])
            )
        )
        result_x = result.first()
        if result_x is None:
            return None
        return self._row_to_entity(result_x)

    async def find_all(
        self, prefix: EntityId | list[EntityId]
    ) -> list[HabitStreakMark]:
        """Find all streak marks."""
        result = await self._connection.execute(
            select(self._habit_streak_mark_table).where(
                self._habit_streak_mark_table.c.habit_ref_id.in_(
                    [prefix.as_int()]
                    if isinstance(prefix, EntityId)
                    else [p.as_int() for p in prefix]
                )
            )
        )
        results = result.fetchall()
        return [self._row_to_entity(row) for row in results]

    async def upsert(self, habit_streak_mark: HabitStreakMark) -> None:
        """Upsert a habit streak mark."""
        query = (
            update(self._habit_streak_mark_table)
            .where(
                self._habit_streak_mark_table.c.habit_ref_id
                == habit_streak_mark.habit.as_int()
            )
            .where(
                self._habit_streak_mark_table.c.date
                == self._realm_codec_registry.db_encode(habit_streak_mark.date)
            )
            .values(
                **(
                    cast(
                        Mapping[str, RealmThing],
                        self._realm_codec_registry.db_encode(habit_streak_mark),
                    )
                ),
            )
        )
        result = await self._connection.execute(query)
        if result.rowcount == 0:
            await self.create(habit_streak_mark)

    async def find_all_between_dates(
        self, habit_ref_id: EntityId, start_date: ADate, end_date: ADate
    ) -> list[HabitStreakMark]:
        """Find all streak marks between two dates."""
        result = await self._connection.execute(
            select(self._habit_streak_mark_table)
            .where(
                self._habit_streak_mark_table.c.habit_ref_id == habit_ref_id.as_int()
            )
            .where(
                self._habit_streak_mark_table.c.date
                >= self._realm_codec_registry.db_encode(start_date)
            )
            .where(
                self._habit_streak_mark_table.c.date
                <= self._realm_codec_registry.db_encode(end_date)
            )
        )
        results = result.fetchall()
        return [self._row_to_entity(row) for row in results]

    def _row_to_entity(self, row: RowType) -> HabitStreakMark:
        """Convert a row to an entity."""
        return self._realm_codec_registry.db_decode(
            HabitStreakMark, cast(Mapping[str, RealmThing], row._mapping)
        )
