"""The SQLite base habits repository."""
from typing import Optional, Iterable, Final

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, String, Unicode, \
    ForeignKey, update, select, delete
from sqlalchemy.engine import Connection, Result

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.habits.infra.habit_collection_repository \
    import HabitCollectionRepository, HabitCollectionNotFoundError
from jupiter.domain.habits.infra.habit_repository import HabitRepository, \
    HabitNotFoundError
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import upsert_events, build_event_table, remove_events


class SqliteHabitCollectionRepository(HabitCollectionRepository):
    """The habit collection repository."""

    _connection: Final[Connection]
    _habit_collection_table: Final[Table]
    _habit_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._habit_collection_table = Table(
            'habit_collection',
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
        self._habit_collection_event_table = build_event_table(self._habit_collection_table, metadata)

    def create(self, habit_collection: HabitCollection) -> HabitCollection:
        """Create a habit collection."""
        result = self._connection.execute(
            insert(self._habit_collection_table).values(
                ref_id=
                habit_collection.ref_id.as_int() if habit_collection.ref_id != BAD_REF_ID else None,
                version=habit_collection.version,
                archived=habit_collection.archived,
                created_time=habit_collection.created_time.to_db(),
                last_modified_time=habit_collection.last_modified_time.to_db(),
                archived_time=
                habit_collection.archived_time.to_db() if habit_collection.archived_time else None,
                workspace_ref_id=habit_collection.workspace_ref_id.as_int()))
        habit_collection = \
            habit_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._habit_collection_event_table, habit_collection)
        return habit_collection

    def save(self, habit_collection: HabitCollection) -> HabitCollection:
        """Save a habit collection."""
        result = self._connection.execute(
            update(self._habit_collection_table)
            .where(self._habit_collection_table.c.ref_id == habit_collection.ref_id.as_int())
            .values(
                version=habit_collection.version,
                archived=habit_collection.archived,
                created_time=habit_collection.created_time.to_db(),
                last_modified_time=habit_collection.last_modified_time.to_db(),
                archived_time=
                habit_collection.archived_time.to_db() if habit_collection.archived_time else None,
                workspace_ref_id=habit_collection.workspace_ref_id.as_int()))
        if result.rowcount == 0:
            raise HabitCollectionNotFoundError("The habit collection does not exist")
        upsert_events(self._connection, self._habit_collection_event_table, habit_collection)
        return habit_collection

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> HabitCollection:
        """Retrieve a habit collection."""
        query_stmt = \
            select(self._habit_collection_table)\
            .where(self._habit_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._habit_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise HabitCollectionNotFoundError(f"Habit collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_workspace(self, workspace_ref_id: EntityId) -> HabitCollection:
        """Retrieve a habit collection for a project."""
        query_stmt = \
            select(self._habit_collection_table)\
            .where(self._habit_collection_table.c.workspace_ref_id == workspace_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise HabitCollectionNotFoundError(
                f"Habit collection for workspace {workspace_ref_id} does not exist")
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> HabitCollection:
        return HabitCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])))


class SqliteHabitRepository(HabitRepository):
    """Sqlite based habit repository."""

    _connection: Final[Connection]
    _habit_table: Final[Table]
    _habit_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._habit_table = Table(
            'habit',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column(
                'habit_collection_ref_id', Integer, ForeignKey("habit_collection.ref_id"),
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
            Column('skip_rule', String, nullable=True),
            Column('repeats_in_period_count', Integer, nullable=True),
            Column('suspended', Boolean, nullable=False),
            keep_existing=True)
        self._habit_event_table = build_event_table(self._habit_table, metadata)

    def create(self, habit: Habit) -> Habit:
        """Create a habit."""
        result = self._connection.execute(
            insert(self._habit_table)\
                .values(
                    ref_id=habit.ref_id.as_int() if habit.ref_id != BAD_REF_ID else None,
                    version=habit.version,
                    archived=habit.archived,
                    created_time=habit.created_time.to_db(),
                    last_modified_time=habit.last_modified_time.to_db(),
                    archived_time=habit.archived_time.to_db() if habit.archived_time else None,
                    habit_collection_ref_id=habit.habit_collection_ref_id.as_int(),
                    project_ref_id=habit.project_ref_id.as_int(),
                    name=str(habit.name),
                    gen_params_period=habit.gen_params.period.value if habit.gen_params else None,
                    gen_params_eisen=habit.gen_params.eisen.value if habit.gen_params else None,
                    gen_params_difficulty=habit.gen_params.difficulty.value if habit.gen_params.difficulty else None,
                    gen_params_actionable_from_day=
                    habit.gen_params.actionable_from_day.as_int() if habit.gen_params.actionable_from_day else None,
                    gen_params_actionable_from_month=
                    habit.gen_params.actionable_from_month.as_int() if habit.gen_params.actionable_from_month else None,
                    gen_params_due_at_time=str(habit.gen_params.due_at_time) if habit.gen_params.due_at_time else None,
                    gen_params_due_at_day=habit.gen_params.due_at_day.as_int() if habit.gen_params.due_at_day else None,
                    gen_params_due_at_month=
                    habit.gen_params.due_at_month.as_int() if habit.gen_params.due_at_month else None,
                    skip_rule=str(habit.skip_rule) if habit.skip_rule else None,
                    repeats_in_period_count=habit.repeats_in_period_count,
                    suspended=habit.suspended))
        habit = habit.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._habit_event_table, habit)
        return habit

    def save(self, habit: Habit) -> Habit:
        """Save a habit."""
        result = self._connection.execute(
            update(self._habit_table)
            .where(self._habit_table.c.ref_id == habit.ref_id.as_int())
            .values(
                ref_id=habit.ref_id.as_int() if habit.ref_id != BAD_REF_ID else None,
                version=habit.version,
                archived=habit.archived,
                created_time=habit.created_time.to_db(),
                last_modified_time=habit.last_modified_time.to_db(),
                archived_time=habit.archived_time.to_db() if habit.archived_time else None,
                habit_collection_ref_id=habit.habit_collection_ref_id.as_int(),
                project_ref_id=habit.project_ref_id.as_int(),
                name=str(habit.name),
                gen_params_period=habit.gen_params.period.value if habit.gen_params else None,
                gen_params_eisen=habit.gen_params.eisen.value if habit.gen_params else None,
                gen_params_difficulty=habit.gen_params.difficulty.value if habit.gen_params.difficulty else None,
                gen_params_actionable_from_day=
                habit.gen_params.actionable_from_day.as_int() if habit.gen_params.actionable_from_day else None,
                gen_params_actionable_from_month=
                habit.gen_params.actionable_from_month.as_int() if habit.gen_params.actionable_from_month else None,
                gen_params_due_at_time=str(habit.gen_params.due_at_time) if habit.gen_params.due_at_time else None,
                gen_params_due_at_day=habit.gen_params.due_at_day.as_int() if habit.gen_params.due_at_day else None,
                gen_params_due_at_month=
                habit.gen_params.due_at_month.as_int() if habit.gen_params.due_at_month else None,
                repeats_in_period_count=habit.repeats_in_period_count,
                skip_rule=str(habit.skip_rule) if habit.skip_rule else None,
                suspended=habit.suspended))
        if result.rowcount == 0:
            raise HabitNotFoundError(f"Habit with id {habit.ref_id} does not exist")
        upsert_events(self._connection, self._habit_event_table, habit)
        return habit

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Habit:
        """Retrieve a habit."""
        query_stmt = select(self._habit_table).where(self._habit_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._habit_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise HabitNotFoundError(f"Habit with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            habit_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[Habit]:
        """Retrieve habit."""
        query_stmt = \
            select(self._habit_table) \
            .where(
                self._habit_table.c.habit_collection_ref_id
                == habit_collection_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._habit_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._habit_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_project_ref_ids:
            query_stmt = \
                query_stmt.where(
                    self._habit_table.c.project_ref_id.in_(fi.as_int() for fi in filter_project_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Habit:
        """Remove a habit."""
        query_stmt = select(self._habit_table).where(self._habit_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise HabitNotFoundError(f"Habit with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._habit_table)
            .where(self._habit_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._habit_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Habit:
        return Habit(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            habit_collection_ref_id=EntityId.from_raw(str(row["habit_collection_ref_id"])),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=HabitName.from_raw(row["name"]),
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
            skip_rule=RecurringTaskSkipRule.from_raw(row["skip_rule"]) if row["skip_rule"] else None,
            repeats_in_period_count=row["repeats_in_period_count"],
            suspended=row["suspended"])
