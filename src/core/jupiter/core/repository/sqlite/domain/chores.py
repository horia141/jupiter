"""The SQLite base chores repository."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionAlreadyExistsError,
    ChoreCollectionNotFoundError,
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import (
    ChoreNotFoundError,
    ChoreRepository,
)
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
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


class SqliteChoreCollectionRepository(ChoreCollectionRepository):
    """The chore collection repository."""

    _connection: Final[AsyncConnection]
    _chore_collection_table: Final[Table]
    _chore_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._chore_collection_table = Table(
            "chore_collection",
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
        self._chore_collection_event_table = build_event_table(
            self._chore_collection_table,
            metadata,
        )

    async def create(self, entity: ChoreCollection) -> ChoreCollection:
        """Create a chore collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._chore_collection_table).values(
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
            raise ChoreCollectionAlreadyExistsError(
                f"Chore collection for workspace {entity.workspace_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._chore_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: ChoreCollection) -> ChoreCollection:
        """Save a chore collection."""
        result = await self._connection.execute(
            update(self._chore_collection_table)
            .where(self._chore_collection_table.c.ref_id == entity.ref_id.as_int())
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
            raise ChoreCollectionNotFoundError("The chore collection does not exist")
        await upsert_events(
            self._connection,
            self._chore_collection_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> ChoreCollection:
        """Retrieve a chore collection."""
        query_stmt = select(self._chore_collection_table).where(
            self._chore_collection_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._chore_collection_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ChoreCollectionNotFoundError(
                f"Chore collection with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> ChoreCollection:
        """Retrieve a chore collection for a project."""
        query_stmt = select(self._chore_collection_table).where(
            self._chore_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ChoreCollectionNotFoundError(
                f"Chore collection for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> ChoreCollection:
        return ChoreCollection(
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


class SqliteChoreRepository(ChoreRepository):
    """Sqlite based chore repository."""

    _connection: Final[AsyncConnection]
    _chore_table: Final[Table]
    _chore_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._chore_table = Table(
            "chore",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "chore_collection_ref_id",
                Integer,
                ForeignKey("chore_collection.ref_id"),
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
            Column("suspended", Boolean, nullable=False),
            Column("must_do", Boolean, nullable=False),
            Column("skip_rule", String, nullable=True),
            Column("start_at_date", DateTime, nullable=False),
            Column("end_at_date", DateTime, nullable=True),
            keep_existing=True,
        )
        self._chore_event_table = build_event_table(self._chore_table, metadata)

    async def create(self, entity: Chore) -> Chore:
        """Create a chore."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._chore_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                chore_collection_ref_id=entity.chore_collection_ref_id.as_int(),
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
                suspended=entity.suspended,
                must_do=entity.must_do,
                skip_rule=str(entity.skip_rule) if entity.skip_rule else None,
                start_at_date=entity.start_at_date.to_db(),
                end_at_date=entity.end_at_date.to_db() if entity.end_at_date else None,
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._chore_event_table, entity)
        return entity

    async def save(self, entity: Chore) -> Chore:
        """Save a chore."""
        result = await self._connection.execute(
            update(self._chore_table)
            .where(self._chore_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                chore_collection_ref_id=entity.chore_collection_ref_id.as_int(),
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
                suspended=entity.suspended,
                must_do=entity.must_do,
                skip_rule=str(entity.skip_rule) if entity.skip_rule else None,
                start_at_date=entity.start_at_date.to_db(),
                end_at_date=entity.end_at_date.to_db() if entity.end_at_date else None,
            ),
        )
        if result.rowcount == 0:
            raise ChoreNotFoundError(f"Chore with id {entity.ref_id} does not exist")
        await upsert_events(self._connection, self._chore_event_table, entity)
        return entity

    async def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Chore:
        """Retrieve a chore."""
        query_stmt = select(self._chore_table).where(
            self._chore_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ChoreNotFoundError(f"Chore with id {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Chore]:
        """Retrieve chore."""
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
    ) -> List[Chore]:
        """Retrieve chore."""
        query_stmt = select(self._chore_table).where(
            self._chore_table.c.chore_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._chore_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_project_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._chore_table.c.project_ref_id.in_(
                    fi.as_int() for fi in filter_project_ref_ids
                ),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[Chore]:
        """Find all chores with generic filters."""
        query_stmt = select(self._chore_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_table.c.archived.is_(False))

        query_stmt = compile_query_relative_to(query_stmt, self._chore_table, kwargs)

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Chore:
        """Remove a chore."""
        query_stmt = select(self._chore_table).where(
            self._chore_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ChoreNotFoundError(f"Chore with id {ref_id} does not exist")
        await self._connection.execute(
            delete(self._chore_table).where(
                self._chore_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._chore_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Chore:
        return Chore(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            chore_collection_ref_id=EntityId.from_raw(
                str(row["chore_collection_ref_id"]),
            ),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=ChoreName.from_raw(row["name"]),
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
            suspended=row["suspended"],
            must_do=row["must_do"],
            skip_rule=RecurringTaskSkipRule.from_raw(row["skip_rule"])
            if row["skip_rule"]
            else None,
            start_at_date=ADate.from_db(row["start_at_date"]),
            end_at_date=ADate.from_db(row["end_at_date"])
            if row["end_at_date"]
            else None,
        )
