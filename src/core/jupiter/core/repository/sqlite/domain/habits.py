"""The SQLite base habits repository."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionAlreadyExistsError,
    HabitCollectionNotFoundError,
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import (
    HabitNotFoundError,
    HabitRepository,
)
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
    Unicode,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteHabitCollectionRepository(HabitCollectionRepository):
    """The habit collection repository."""

    _connection: Final[AsyncConnection]
    _habit_collection_table: Final[Table]
    _habit_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._habit_collection_table = Table(
            "habit_collection",
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
                ForeignKey("workspace_ref_id.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            keep_existing=True,
        )
        self._habit_collection_event_table = build_event_table(
            self._habit_collection_table,
            metadata,
        )

    async def create(self, entity: HabitCollection) -> HabitCollection:
        """Create a habit collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._habit_collection_table).values(
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
            raise HabitCollectionAlreadyExistsError(
                f"Habit collection for workspace {entity.workspace_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._habit_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: HabitCollection) -> HabitCollection:
        """Save a habit collection."""
        result = await self._connection.execute(
            update(self._habit_collection_table)
            .where(self._habit_collection_table.c.ref_id == entity.ref_id.as_int())
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
            raise HabitCollectionNotFoundError("The habit collection does not exist")
        await upsert_events(
            self._connection,
            self._habit_collection_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> HabitCollection:
        """Retrieve a habit collection."""
        query_stmt = select(self._habit_collection_table).where(
            self._habit_collection_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._habit_collection_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise HabitCollectionNotFoundError(
                f"Habit collection with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> HabitCollection:
        """Retrieve a habit collection for a project."""
        query_stmt = select(self._habit_collection_table).where(
            self._habit_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise HabitCollectionNotFoundError(
                f"Habit collection for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> HabitCollection:
        return HabitCollection(
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


class SqliteHabitRepository(HabitRepository):
    """Sqlite based habit repository."""

    _connection: Final[AsyncConnection]
    _habit_table: Final[Table]
    _habit_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._habit_table = Table(
            "habit",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "habit_collection_ref_id",
                Integer,
                ForeignKey("habit_collection.ref_id"),
                nullable=False,
            ),
            Column(
                "project_ref_id",
                Integer,
                ForeignKey("project.ref_id"),
                nullable=False,
                index=True,
            ),
            Column("name", Unicode(), nullable=False),
            Column("gen_params_period", String, nullable=False),
            Column("gen_params_eisen", String, nullable=True),
            Column("gen_params_difficulty", String, nullable=True),
            Column("gen_params_actionable_from_day", Integer, nullable=True),
            Column("gen_params_actionable_from_month", Integer, nullable=True),
            Column("gen_params_due_at_time", String, nullable=True),
            Column("gen_params_due_at_day", Integer, nullable=True),
            Column("gen_params_due_at_month", Integer, nullable=True),
            Column("skip_rule", String, nullable=True),
            Column("repeats_in_period_count", Integer, nullable=True),
            Column("suspended", Boolean, nullable=False),
            keep_existing=True,
        )
        self._habit_event_table = build_event_table(self._habit_table, metadata)

    async def create(self, entity: Habit) -> Habit:
        """Create a habit."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._habit_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                habit_collection_ref_id=entity.habit_collection_ref_id.as_int(),
                project_ref_id=entity.project_ref_id.as_int(),
                name=str(entity.name),
                gen_params_period=entity.gen_params.period.value
                if entity.gen_params
                else None,
                gen_params_eisen=entity.gen_params.eisen.value
                if entity.gen_params.eisen
                else None,
                gen_params_difficulty=entity.gen_params.difficulty.value
                if entity.gen_params.difficulty
                else None,
                gen_params_actionable_from_day=entity.gen_params.actionable_from_day.as_int()
                if entity.gen_params.actionable_from_day
                else None,
                gen_params_actionable_from_month=entity.gen_params.actionable_from_month.as_int()
                if entity.gen_params.actionable_from_month
                else None,
                gen_params_due_at_time=str(entity.gen_params.due_at_time)
                if entity.gen_params.due_at_time
                else None,
                gen_params_due_at_day=entity.gen_params.due_at_day.as_int()
                if entity.gen_params.due_at_day
                else None,
                gen_params_due_at_month=entity.gen_params.due_at_month.as_int()
                if entity.gen_params.due_at_month
                else None,
                skip_rule=str(entity.skip_rule) if entity.skip_rule else None,
                repeats_in_period_count=entity.repeats_in_period_count,
                suspended=entity.suspended,
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._habit_event_table, entity)
        return entity

    async def save(self, entity: Habit) -> Habit:
        """Save a habit."""
        result = await self._connection.execute(
            update(self._habit_table)
            .where(self._habit_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                habit_collection_ref_id=entity.habit_collection_ref_id.as_int(),
                project_ref_id=entity.project_ref_id.as_int(),
                name=str(entity.name),
                gen_params_period=entity.gen_params.period.value
                if entity.gen_params
                else None,
                gen_params_eisen=entity.gen_params.eisen.value
                if entity.gen_params.eisen
                else None,
                gen_params_difficulty=entity.gen_params.difficulty.value
                if entity.gen_params.difficulty
                else None,
                gen_params_actionable_from_day=entity.gen_params.actionable_from_day.as_int()
                if entity.gen_params.actionable_from_day
                else None,
                gen_params_actionable_from_month=entity.gen_params.actionable_from_month.as_int()
                if entity.gen_params.actionable_from_month
                else None,
                gen_params_due_at_time=str(entity.gen_params.due_at_time)
                if entity.gen_params.due_at_time
                else None,
                gen_params_due_at_day=entity.gen_params.due_at_day.as_int()
                if entity.gen_params.due_at_day
                else None,
                gen_params_due_at_month=entity.gen_params.due_at_month.as_int()
                if entity.gen_params.due_at_month
                else None,
                repeats_in_period_count=entity.repeats_in_period_count,
                skip_rule=str(entity.skip_rule) if entity.skip_rule else None,
                suspended=entity.suspended,
            ),
        )
        if result.rowcount == 0:
            raise HabitNotFoundError(f"Habit with id {entity.ref_id} does not exist")
        await upsert_events(self._connection, self._habit_event_table, entity)
        return entity

    async def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Habit:
        """Retrieve a habit."""
        query_stmt = select(self._habit_table).where(
            self._habit_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._habit_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise HabitNotFoundError(f"Habit with id {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Habit]:
        """Retrieve habit."""
        return await self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids,
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Habit]:
        """Retrieve habit."""
        query_stmt = select(self._habit_table).where(
            self._habit_table.c.habit_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._habit_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._habit_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_project_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._habit_table.c.project_ref_id.in_(
                    fi.as_int() for fi in filter_project_ref_ids
                ),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Habit:
        """Remove a habit."""
        query_stmt = select(self._habit_table).where(
            self._habit_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise HabitNotFoundError(f"Habit with id {ref_id} does not exist")
        await self._connection.execute(
            delete(self._habit_table).where(
                self._habit_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._habit_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Habit:
        return Habit(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            habit_collection_ref_id=EntityId.from_raw(
                str(row["habit_collection_ref_id"]),
            ),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=HabitName.from_raw(row["name"]),
            gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["gen_params_period"]),
                eisen=Eisen.from_raw(row["gen_params_eisen"])
                if row["gen_params_eisen"]
                else None,
                difficulty=Difficulty.from_raw(row["gen_params_difficulty"])
                if row["gen_params_difficulty"]
                else None,
                actionable_from_day=RecurringTaskDueAtDay(
                    row["gen_params_actionable_from_day"],
                )
                if row["gen_params_actionable_from_day"] is not None
                else None,
                actionable_from_month=RecurringTaskDueAtMonth(
                    row["gen_params_actionable_from_month"],
                )
                if row["gen_params_actionable_from_month"] is not None
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(
                    row["gen_params_due_at_time"],
                )
                if row["gen_params_due_at_time"] is not None
                else None,
                due_at_day=RecurringTaskDueAtDay(row["gen_params_due_at_day"])
                if row["gen_params_due_at_day"] is not None
                else None,
                due_at_month=RecurringTaskDueAtMonth(row["gen_params_due_at_month"])
                if row["gen_params_due_at_month"] is not None
                else None,
            ),
            skip_rule=RecurringTaskSkipRule.from_raw(row["skip_rule"])
            if row["skip_rule"]
            else None,
            repeats_in_period_count=row["repeats_in_period_count"],
            suspended=row["suspended"],
        )
