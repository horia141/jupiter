"""The SQLite base chores repository."""
from typing import Optional, Iterable, Final

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, String, Unicode, \
    ForeignKey, update, select, delete
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.domain.chores.chore_name import ChoreName
from jupiter.domain.chores.infra.chore_collection_repository \
    import ChoreCollectionRepository, ChoreCollectionNotFoundError
from jupiter.domain.chores.infra.chore_repository import ChoreRepository, \
    ChoreNotFoundError
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import upsert_events, build_event_table, remove_events


class SqliteChoreCollectionRepository(ChoreCollectionRepository):
    """The chore collection repository."""

    _connection: Final[Connection]
    _chore_collection_table: Final[Table]
    _chore_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._chore_collection_table = Table(
            'chore_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'workspace_ref_id', Integer, ForeignKey("workspace_ref_id.ref_id"),
                unique=True, index=True, nullable=False),
            keep_existing=True)
        self._chore_collection_event_table = build_event_table(self._chore_collection_table, metadata)

    def create(self, chore_collection: ChoreCollection) -> ChoreCollection:
        """Create a chore collection."""
        result = self._connection.execute(
            insert(self._chore_collection_table).values(
                ref_id=
                chore_collection.ref_id.as_int() if chore_collection.ref_id != BAD_REF_ID else None,
                version=chore_collection.version,
                archived=chore_collection.archived,
                created_time=chore_collection.created_time.to_db(),
                last_modified_time=chore_collection.last_modified_time.to_db(),
                archived_time=
                chore_collection.archived_time.to_db() if chore_collection.archived_time else None,
                workspace_ref_id=chore_collection.workspace_ref_id.as_int()))
        chore_collection = \
            chore_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._chore_collection_event_table, chore_collection)
        return chore_collection

    def save(self, chore_collection: ChoreCollection) -> ChoreCollection:
        """Save a chore collection."""
        result = self._connection.execute(
            update(self._chore_collection_table)
            .where(self._chore_collection_table.c.ref_id == chore_collection.ref_id.as_int())
            .values(
                version=chore_collection.version,
                archived=chore_collection.archived,
                created_time=chore_collection.created_time.to_db(),
                last_modified_time=chore_collection.last_modified_time.to_db(),
                archived_time=
                chore_collection.archived_time.to_db() if chore_collection.archived_time else None,
                workspace_ref_id=chore_collection.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise ChoreCollectionNotFoundError("The chore collection does not exist")
        upsert_events(self._connection, self._chore_collection_event_table, chore_collection)
        return chore_collection

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> ChoreCollection:
        """Retrieve a chore collection."""
        query_stmt = \
            select(self._chore_collection_table)\
            .where(self._chore_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ChoreCollectionNotFoundError(f"Chore collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_workspace(self, workspace_ref_id: EntityId) -> ChoreCollection:
        """Retrieve a chore collection for a project."""
        query_stmt = \
            select(self._chore_collection_table)\
            .where(self._chore_collection_table.c.workspace_ref_id == workspace_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ChoreCollectionNotFoundError(
                f"Chore collection for workspace {workspace_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> ChoreCollection:
        return ChoreCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteChoreRepository(ChoreRepository):
    """Sqlite based chore repository."""

    _connection: Final[Connection]
    _chore_table: Final[Table]
    _chore_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._chore_table = Table(
            'chore',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'chore_collection_ref_id', Integer, ForeignKey("chore_collection.ref_id"),
                nullable=False),
            Column('project_ref_id', Integer, ForeignKey('project.ref_id'), nullable=False, index=True),
            Column('name', Unicode(), nullable=False),
            Column('gen_params_period', String, nullable=False),
            Column('gen_params_eisen', String, nullable=True),
            Column('gen_params_difficulty', String, nullable=True),
            Column('gen_params_actionable_from_day', Integer, nullable=True),
            Column('gen_params_actionable_from_month', Integer, nullable=True),
            Column('gen_params_due_at_time', String, nullable=True),
            Column('gen_params_due_at_day', Integer, nullable=True),
            Column('gen_params_due_at_month', Integer, nullable=True),
            Column('suspended', Boolean, nullable=False),
            Column('must_do', Boolean, nullable=False),
            Column('skip_rule', String, nullable=True),
            Column('start_at_date', DateTime, nullable=False),
            Column('end_at_date', DateTime, nullable=True),
            keep_existing=True)
        self._chore_event_table = build_event_table(self._chore_table, metadata)

    def create(self, chore: Chore) -> Chore:
        """Create a chore."""
        result = self._connection.execute(
            insert(self._chore_table)\
                .values(
                    ref_id=chore.ref_id.as_int() if chore.ref_id != BAD_REF_ID else None,
                    version=chore.version,
                    archived=chore.archived,
                    created_time=chore.created_time.to_db(),
                    last_modified_time=chore.last_modified_time.to_db(),
                    archived_time=chore.archived_time.to_db() if chore.archived_time else None,
                    chore_collection_ref_id=chore.chore_collection_ref_id.as_int(),
                    project_ref_id=chore.project_ref_id.as_int(),
                    name=str(chore.name),
                    gen_params_period=chore.gen_params.period.value if chore.gen_params else None,
                    gen_params_eisen=chore.gen_params.eisen.value if chore.gen_params else None,
                    gen_params_difficulty=chore.gen_params.difficulty.value
                    if chore.gen_params and chore.gen_params.difficulty else None,
                    gen_params_actionable_from_day=chore.gen_params.actionable_from_day.as_int()
                    if chore.gen_params and chore.gen_params.actionable_from_day else None,
                    gen_params_actionable_from_month=chore.gen_params.actionable_from_month.as_int()
                    if chore.gen_params and chore.gen_params.actionable_from_month else None,
                    gen_params_due_at_time=str(chore.gen_params.due_at_time)
                    if chore.gen_params and chore.gen_params.due_at_time else None,
                    gen_params_due_at_day=chore.gen_params.due_at_day.as_int()
                    if chore.gen_params and chore.gen_params.due_at_day else None,
                    gen_params_due_at_month=chore.gen_params.due_at_month.as_int()
                    if chore.gen_params and chore.gen_params.due_at_month else None,
                    suspended=chore.suspended,
                    must_do=chore.must_do,
                    skip_rule=str(chore.skip_rule) if chore.skip_rule else None,
                    start_at_date=chore.start_at_date.to_db(),
                    end_at_date=chore.end_at_date.to_db() if chore.end_at_date else None))
        chore = chore.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._chore_event_table, chore)
        return chore

    def save(self, chore: Chore) -> Chore:
        """Save a chore."""
        result = self._connection.execute(
            update(self._chore_table)
            .where(self._chore_table.c.ref_id == chore.ref_id.as_int())
            .values(
                ref_id=chore.ref_id.as_int() if chore.ref_id != BAD_REF_ID else None,
                version=chore.version,
                archived=chore.archived,
                created_time=chore.created_time.to_db(),
                last_modified_time=chore.last_modified_time.to_db(),
                archived_time=chore.archived_time.to_db() if chore.archived_time else None,
                chore_collection_ref_id=chore.chore_collection_ref_id.as_int(),
                project_ref_id=chore.project_ref_id.as_int(),
                name=str(chore.name),
                gen_params_period=chore.gen_params.period.value if chore.gen_params else None,
                gen_params_eisen=chore.gen_params.eisen.value if chore.gen_params else None,
                gen_params_difficulty=chore.gen_params.difficulty.value
                if chore.gen_params and chore.gen_params.difficulty else None,
                gen_params_actionable_from_day=chore.gen_params.actionable_from_day.as_int()
                if chore.gen_params and chore.gen_params.actionable_from_day else None,
                gen_params_actionable_from_month=chore.gen_params.actionable_from_month.as_int()
                if chore.gen_params and chore.gen_params.actionable_from_month else None,
                gen_params_due_at_time=str(chore.gen_params.due_at_time)
                if chore.gen_params and chore.gen_params.due_at_time else None,
                gen_params_due_at_day=chore.gen_params.due_at_day.as_int()
                if chore.gen_params and chore.gen_params.due_at_day else None,
                gen_params_due_at_month=chore.gen_params.due_at_month.as_int()
                if chore.gen_params and chore.gen_params.due_at_month else None,
                suspended=chore.suspended,
                must_do=chore.must_do,
                skip_rule=str(chore.skip_rule) if chore.skip_rule else None,
                start_at_date=chore.start_at_date.to_db(),
                end_at_date=chore.end_at_date.to_db() if chore.end_at_date else None))
        if result.rowcount == 0:
            raise ChoreNotFoundError(f"Chore with id {chore.ref_id} does not exist")
        upsert_events(self._connection, self._chore_event_table, chore)
        return chore

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Chore:
        """Retrieve a chore."""
        query_stmt = select(self._chore_table).where(self._chore_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ChoreNotFoundError(f"Chore with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            chore_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[Chore]:
        """Retrieve chore."""
        query_stmt = \
            select(self._chore_table) \
            .where(
                self._chore_table.c.chore_collection_ref_id
                == chore_collection_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._chore_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._chore_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_project_ref_ids:
            query_stmt = \
                query_stmt.where(
                    self._chore_table.c.project_ref_id.in_(fi.as_int() for fi in filter_project_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Chore:
        """Remove a chore."""
        query_stmt = select(self._chore_table).where(self._chore_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise ChoreNotFoundError(f"Chore with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._chore_table)
            .where(self._chore_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._chore_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Chore:
        return Chore(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            chore_collection_ref_id=EntityId.from_raw(str(row["chore_collection_ref_id"])),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=ChoreName.from_raw(row["name"]),
            gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["gen_params_period"]),
                eisen=Eisen.from_raw(row["gen_params_eisen"]),
                difficulty=Difficulty.from_raw(row["gen_params_difficulty"])
                if row["gen_params_difficulty"] else None,
                actionable_from_day=RecurringTaskDueAtDay(row["gen_params_actionable_from_day"])
                if row["gen_params_actionable_from_day"] is not None else None,
                actionable_from_month=RecurringTaskDueAtMonth(row["gen_params_actionable_from_month"])
                if row["gen_params_actionable_from_month"] is not None else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(row["gen_params_due_at_time"])
                if row["gen_params_due_at_time"] is not None else None,
                due_at_day=RecurringTaskDueAtDay(row["gen_params_due_at_day"])
                if row["gen_params_due_at_day"] is not None else None,
                due_at_month=RecurringTaskDueAtMonth(row["gen_params_due_at_month"])
                if row["gen_params_due_at_month"] is not None else None),
            suspended=row["suspended"],
            must_do=row["must_do"],
            skip_rule=RecurringTaskSkipRule.from_raw(row["skip_rule"]) if row["skip_rule"] else None,
            start_at_date=ADate.from_db(row["start_at_date"]),
            end_at_date=ADate.from_db(row["end_at_date"]) if row["end_at_date"] else None)
