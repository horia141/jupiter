"""The SQLite base recurring tasks repository."""
from typing import Optional, Iterable, Final

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, String, Unicode, \
    ForeignKey, update, select, delete
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.infra.recurring_task_collection_repository \
    import RecurringTaskCollectionRepository, RecurringTaskCollectionNotFoundError
from jupiter.domain.recurring_tasks.infra.recurring_task_repository import RecurringTaskRepository, \
    RecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import upsert_events, build_event_table, remove_events


class SqliteRecurringTaskCollectionRepository(RecurringTaskCollectionRepository):
    """The recurring task collection repository."""

    _connection: Final[Connection]
    _recurring_task_collection_table: Final[Table]
    _recurring_task_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._recurring_task_collection_table = Table(
            'recurring_task_collection',
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
        self._recurring_task_collection_event_table = build_event_table(self._recurring_task_collection_table, metadata)

    def create(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Create a recurring task collection."""
        result = self._connection.execute(
            insert(self._recurring_task_collection_table).values(
                ref_id=
                recurring_task_collection.ref_id.as_int() if recurring_task_collection.ref_id != BAD_REF_ID else None,
                version=recurring_task_collection.version,
                archived=recurring_task_collection.archived,
                created_time=recurring_task_collection.created_time.to_db(),
                last_modified_time=recurring_task_collection.last_modified_time.to_db(),
                archived_time=
                recurring_task_collection.archived_time.to_db() if recurring_task_collection.archived_time else None,
                workspace_ref_id=recurring_task_collection.workspace_ref_id.as_int()))
        recurring_task_collection = \
            recurring_task_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._recurring_task_collection_event_table, recurring_task_collection)
        return recurring_task_collection

    def save(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Save a recurring task collection."""
        result = self._connection.execute(
            update(self._recurring_task_collection_table)
            .where(self._recurring_task_collection_table.c.ref_id == recurring_task_collection.ref_id.as_int())
            .values(
                version=recurring_task_collection.version,
                archived=recurring_task_collection.archived,
                created_time=recurring_task_collection.created_time.to_db(),
                last_modified_time=recurring_task_collection.last_modified_time.to_db(),
                archived_time=
                recurring_task_collection.archived_time.to_db() if recurring_task_collection.archived_time else None,
                workspace_ref_id=recurring_task_collection.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise RecurringTaskCollectionNotFoundError("The recurring task collection does not exist")
        upsert_events(self._connection, self._recurring_task_collection_event_table, recurring_task_collection)
        return recurring_task_collection

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTaskCollection:
        """Retrieve a recurring task collection."""
        query_stmt = \
            select(self._recurring_task_collection_table)\
            .where(self._recurring_task_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._recurring_task_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise RecurringTaskCollectionNotFoundError(f"Recurring task collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_workspace(self, workspace_ref_id: EntityId) -> RecurringTaskCollection:
        """Retrieve a recurring task collection for a project."""
        query_stmt = \
            select(self._recurring_task_collection_table)\
            .where(self._recurring_task_collection_table.c.workspace_ref_id == workspace_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise RecurringTaskCollectionNotFoundError(
                f"Recurring task collection for workspace {workspace_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> RecurringTaskCollection:
        return RecurringTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteRecurringTaskRepository(RecurringTaskRepository):
    """Sqlite based recurring task repository."""

    _connection: Final[Connection]
    _recurring_task_table: Final[Table]
    _recurring_task_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._recurring_task_table = Table(
            'recurring_task',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'recurring_task_collection_ref_id', Integer, ForeignKey("recurring_task_collection.ref_id"),
                nullable=False),
            Column('project_ref_id', Integer, ForeignKey('project.ref_id'), nullable=False, index=True),
            Column('name', Unicode(), nullable=False),
            Column('the_type', String(16), nullable=False),
            Column('gen_params_period', String, nullable=False),
            Column('gen_params_eisen', String, nullable=True),
            Column('gen_params_difficulty', String, nullable=True),
            Column('gen_params_actionable_from_day', Integer, nullable=True),
            Column('gen_params_actionable_from_month', Integer, nullable=True),
            Column('gen_params_due_at_time', String, nullable=True),
            Column('gen_params_due_at_day', Integer, nullable=True),
            Column('gen_params_due_at_month', Integer, nullable=True),
            Column('suspended', Boolean, nullable=False),
            Column('skip_rule', String, nullable=True),
            Column('must_do', Boolean, nullable=False),
            Column('start_at_date', DateTime, nullable=False),
            Column('end_at_date', DateTime, nullable=True),
            keep_existing=True)
        self._recurring_task_event_table = build_event_table(self._recurring_task_table, metadata)

    def create(self, recurring_task: RecurringTask) -> RecurringTask:
        """Create a recurring task."""
        result = self._connection.execute(
            insert(self._recurring_task_table)\
                .values(
                    ref_id=recurring_task.ref_id.as_int() if recurring_task.ref_id != BAD_REF_ID else None,
                    version=recurring_task.version,
                    archived=recurring_task.archived,
                    created_time=recurring_task.created_time.to_db(),
                    last_modified_time=recurring_task.last_modified_time.to_db(),
                    archived_time=recurring_task.archived_time.to_db() if recurring_task.archived_time else None,
                    recurring_task_collection_ref_id=recurring_task.recurring_task_collection_ref_id.as_int(),
                    project_ref_id=recurring_task.project_ref_id.as_int(),
                    name=str(recurring_task.name),
                    the_type=str(recurring_task.the_type),
                    gen_params_period=recurring_task.gen_params.period.value if recurring_task.gen_params else None,
                    gen_params_eisen=recurring_task.gen_params.eisen.value if recurring_task.gen_params else None,
                    gen_params_difficulty=recurring_task.gen_params.difficulty.value
                    if recurring_task.gen_params and recurring_task.gen_params.difficulty else None,
                    gen_params_actionable_from_day=recurring_task.gen_params.actionable_from_day.as_int()
                    if recurring_task.gen_params and recurring_task.gen_params.actionable_from_day else None,
                    gen_params_actionable_from_month=recurring_task.gen_params.actionable_from_month.as_int()
                    if recurring_task.gen_params and recurring_task.gen_params.actionable_from_month else None,
                    gen_params_due_at_time=str(recurring_task.gen_params.due_at_time)
                    if recurring_task.gen_params and recurring_task.gen_params.due_at_time else None,
                    gen_params_due_at_day=recurring_task.gen_params.due_at_day.as_int()
                    if recurring_task.gen_params and recurring_task.gen_params.due_at_day else None,
                    gen_params_due_at_month=recurring_task.gen_params.due_at_month.as_int()
                    if recurring_task.gen_params and recurring_task.gen_params.due_at_month else None,
                    suspended=recurring_task.suspended,
                    skip_rule=str(recurring_task.skip_rule) if recurring_task.skip_rule else None,
                    must_do=recurring_task.must_do,
                    start_at_date=recurring_task.start_at_date.to_db(),
                    end_at_date=recurring_task.end_at_date.to_db() if recurring_task.end_at_date else None))
        recurring_task = recurring_task.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._recurring_task_event_table, recurring_task)
        return recurring_task

    def save(self, recurring_task: RecurringTask) -> RecurringTask:
        """Save a recurring task."""
        result = self._connection.execute(
            update(self._recurring_task_table)
            .where(self._recurring_task_table.c.ref_id == recurring_task.ref_id.as_int())
            .values(
                ref_id=recurring_task.ref_id.as_int() if recurring_task.ref_id != BAD_REF_ID else None,
                version=recurring_task.version,
                archived=recurring_task.archived,
                created_time=recurring_task.created_time.to_db(),
                last_modified_time=recurring_task.last_modified_time.to_db(),
                archived_time=recurring_task.archived_time.to_db() if recurring_task.archived_time else None,
                recurring_task_collection_ref_id=recurring_task.recurring_task_collection_ref_id.as_int(),
                project_ref_id=recurring_task.project_ref_id.as_int(),
                name=str(recurring_task.name),
                the_type=str(recurring_task.the_type),
                gen_params_period=recurring_task.gen_params.period.value if recurring_task.gen_params else None,
                gen_params_eisen=recurring_task.gen_params.eisen.value if recurring_task.gen_params else None,
                gen_params_difficulty=recurring_task.gen_params.difficulty.value
                if recurring_task.gen_params and recurring_task.gen_params.difficulty else None,
                gen_params_actionable_from_day=recurring_task.gen_params.actionable_from_day.as_int()
                if recurring_task.gen_params and recurring_task.gen_params.actionable_from_day else None,
                gen_params_actionable_from_month=recurring_task.gen_params.actionable_from_month.as_int()
                if recurring_task.gen_params and recurring_task.gen_params.actionable_from_month else None,
                gen_params_due_at_time=str(recurring_task.gen_params.due_at_time)
                if recurring_task.gen_params and recurring_task.gen_params.due_at_time else None,
                gen_params_due_at_day=recurring_task.gen_params.due_at_day.as_int()
                if recurring_task.gen_params and recurring_task.gen_params.due_at_day else None,
                gen_params_due_at_month=recurring_task.gen_params.due_at_month.as_int()
                if recurring_task.gen_params and recurring_task.gen_params.due_at_month else None,
                suspended=recurring_task.suspended,
                skip_rule=str(recurring_task.skip_rule) if recurring_task.skip_rule else None,
                must_do=recurring_task.must_do,
                start_at_date=recurring_task.start_at_date.to_db(),
                end_at_date=recurring_task.end_at_date.to_db() if recurring_task.end_at_date else None))
        if result.rowcount == 0:
            raise RecurringTaskNotFoundError(f"Recurring task with id {recurring_task.ref_id} does not exist")
        upsert_events(self._connection, self._recurring_task_event_table, recurring_task)
        return recurring_task

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTask:
        """Retrieve a recurring task."""
        query_stmt = select(self._recurring_task_table).where(self._recurring_task_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._recurring_task_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise RecurringTaskNotFoundError(f"Recurring task with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            recurring_task_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTask]:
        """Retrieve recurring task."""
        query_stmt = \
            select(self._recurring_task_table) \
            .where(
                self._recurring_task_table.c.recurring_task_collection_ref_id
                == recurring_task_collection_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._recurring_task_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._recurring_task_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_project_ref_ids:
            query_stmt = \
                query_stmt.where(
                    self._recurring_task_table.c.project_ref_id.in_(fi.as_int() for fi in filter_project_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> RecurringTask:
        """Remove a recurring task."""
        query_stmt = select(self._recurring_task_table).where(self._recurring_task_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise RecurringTaskNotFoundError(f"Recurring task with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._recurring_task_table)
            .where(self._recurring_task_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._recurring_task_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> RecurringTask:
        return RecurringTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            recurring_task_collection_ref_id=EntityId.from_raw(str(row["recurring_task_collection_ref_id"])),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=RecurringTaskName.from_raw(row["name"]),
            the_type=RecurringTaskType.from_raw(row["the_type"]),
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
            skip_rule=RecurringTaskSkipRule.from_raw(row["skip_rule"]) if row["skip_rule"] else None,
            must_do=row["must_do"],
            start_at_date=ADate.from_db(row["start_at_date"]),
            end_at_date=ADate.from_db(row["end_at_date"]) if row["end_at_date"] else None)
