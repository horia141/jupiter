"""The SQLite repository for inbox tasks."""
from typing import Optional, Iterable, Final

from sqlalchemy import insert, MetaData, Table, Column, Integer, Boolean, DateTime, ForeignKey, update, select, \
    delete, String, Unicode
from sqlalchemy.engine import Connection, Result

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository, \
    InboxTaskCollectionNotFoundError
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository, InboxTaskNotFoundError
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import upsert_events, build_event_table, remove_events


class SqliteInboxTaskCollectionRepository(InboxTaskCollectionRepository):
    """The inbox task collection repository."""

    _connection: Final[Connection]
    _inbox_task_collection_table: Final[Table]
    _inbox_task_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._inbox_task_collection_table = Table(
            'inbox_task_collection',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('project_ref_id', Integer, ForeignKey("project.ref_id"), unique=True, nullable=False),
            keep_existing=True)
        self._inbox_task_collection_event_table = build_event_table(self._inbox_task_collection_table, metadata)

    def create(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Create the inbox task collection."""
        result = self._connection.execute(
            insert(self._inbox_task_collection_table).values(
                ref_id=inbox_task_collection.ref_id.as_int() if inbox_task_collection.ref_id != BAD_REF_ID else None,
                version=inbox_task_collection.version,
                archived=inbox_task_collection.archived,
                created_time=inbox_task_collection.created_time.to_db(),
                last_modified_time=inbox_task_collection.last_modified_time.to_db(),
                archived_time=
                inbox_task_collection.archived_time.to_db() if inbox_task_collection.archived_time else None,
                project_ref_id=inbox_task_collection.project_ref_id.as_int()))
        inbox_task_collection = inbox_task_collection.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._inbox_task_collection_event_table, inbox_task_collection)
        return inbox_task_collection

    def save(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Save the inbox task collection."""
        result = self._connection.execute(
            update(self._inbox_task_collection_table)
            .where(self._inbox_task_collection_table.c.ref_id == inbox_task_collection.ref_id.as_int())
            .values(
                version=inbox_task_collection.version,
                archived=inbox_task_collection.archived,
                created_time=inbox_task_collection.created_time.to_db(),
                last_modified_time=inbox_task_collection.last_modified_time.to_db(),
                archived_time=
                inbox_task_collection.archived_time.to_db() if inbox_task_collection.archived_time else None,
                project_ref_id=inbox_task_collection.project_ref_id.as_int()))
        if result.rowcount == 0:
            raise InboxTaskCollectionNotFoundError("The inbox task collection does not exist")
        upsert_events(self._connection, self._inbox_task_collection_event_table, inbox_task_collection)
        return inbox_task_collection

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTaskCollection:
        """Retrieve the inbox task collection."""
        query_stmt = \
            select(self._inbox_task_collection_table)\
            .where(self._inbox_task_collection_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._inbox_task_collection_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise InboxTaskCollectionNotFoundError(f"inbox task collection with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def load_by_project(self, project_ref_id: EntityId) -> InboxTaskCollection:
        """Retrieve the inbox task collection for a project."""
        query_stmt = \
            select(self._inbox_task_collection_table)\
                .where(self._inbox_task_collection_table.c.project_ref_id == project_ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise InboxTaskCollectionNotFoundError(f"inbox task collection for project {project_ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTaskCollection]:
        """Retrieve all inbox task collections."""
        query_stmt = select(self._inbox_task_collection_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._inbox_task_collection_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = \
                query_stmt.where(self._inbox_task_collection_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_project_ref_ids:
            query_stmt = \
                query_stmt\
                .where(
                    self._inbox_task_collection_table.c.project_ref_id.in_(
                        fi.as_int() for fi in filter_project_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> InboxTaskCollection:
        """Remove an inbox task collection."""
        query_stmt = \
            select(self._inbox_task_collection_table)\
            .where(self._inbox_task_collection_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise InboxTaskCollectionNotFoundError(f"inbox task collection with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._inbox_task_collection_table)
            .where(self._inbox_task_collection_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._inbox_task_collection_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> InboxTaskCollection:
        return InboxTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])))


class SqliteInboxTaskRepository(InboxTaskRepository):
    """The inbox task repository."""

    _connection: Final[Connection]
    _inbox_task_table: Final[Table]
    _inbox_task_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._inbox_task_table = Table(
            'inbox_task',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('version', Integer, nullable=False),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('inbox_task_collection_ref_id', Integer, ForeignKey("inbox_task_collection.ref_id"), nullable=False),
            Column('source', String(16), nullable=False),
            Column('big_plan_ref_id', Integer, ForeignKey('big_plan.ref_id'), nullable=True),
            Column('recurring_task_ref_id', Integer, ForeignKey('recurring_task.ref_id'), nullable=True),
            Column('metric_ref_id', Integer, ForeignKey('metric.ref_id'), nullable=True),
            Column('person_ref_id', Integer, ForeignKey('person.ref_id'), nullable=True),
            Column('name', Unicode(), nullable=False),
            Column('status', String(16), nullable=False),
            Column('eisen', String(20), nullable=False),
            Column('difficulty', String(10), nullable=True),
            Column('actionable_date', DateTime, nullable=True),
            Column('due_date', DateTime, nullable=True),
            Column('recurring_timeline', String, nullable=True),
            Column('recurring_type', String, nullable=True),
            Column('recurring_gen_right_now', DateTime, nullable=True),
            Column('accepted_time', DateTime, nullable=True),
            Column('working_time', DateTime, nullable=True),
            Column('completed_time', DateTime, nullable=True),
            keep_existing=True)
        self._inbox_task_event_table = build_event_table(self._inbox_task_table, metadata)

    def create(self, inbox_task: InboxTask) -> InboxTask:
        """Create an inbox task."""
        result = self._connection.execute(
            insert(self._inbox_task_table) \
                .values(
                    ref_id=inbox_task.ref_id.as_int() if inbox_task.ref_id != BAD_REF_ID else None,
                    version=inbox_task.version,
                    archived=inbox_task.archived,
                    created_time=inbox_task.created_time.to_db(),
                    last_modified_time=inbox_task.last_modified_time.to_db(),
                    archived_time=inbox_task.archived_time.to_db() if inbox_task.archived_time else None,
                    inbox_task_collection_ref_id=inbox_task.inbox_task_collection_ref_id.as_int(),
                    source=str(inbox_task.source),
                    big_plan_ref_id=inbox_task.big_plan_ref_id.as_int() if inbox_task.big_plan_ref_id else None,
                    recurring_task_ref_id=
                    inbox_task.recurring_task_ref_id.as_int() if inbox_task.recurring_task_ref_id else None,
                    metric_ref_id=inbox_task.metric_ref_id.as_int() if inbox_task.metric_ref_id else None,
                    person_ref_id=inbox_task.person_ref_id.as_int() if inbox_task.person_ref_id else None,
                    name=str(inbox_task.name),
                    status=str(inbox_task.status),
                    eisen=str(inbox_task.eisen),
                    difficulty=str(inbox_task.difficulty) if inbox_task.difficulty else None,
                    actionable_date=inbox_task.actionable_date.to_db() if inbox_task.actionable_date else None,
                    due_date=inbox_task.due_date.to_db() if inbox_task.due_date else None,
                    recurring_timeline=inbox_task.recurring_timeline,
                    recurring_type=str(inbox_task.recurring_type) if inbox_task.recurring_type else None,
                    recurring_gen_right_now=
                    inbox_task.recurring_gen_right_now.to_db() if inbox_task.recurring_gen_right_now else None,
                    accepted_time=inbox_task.accepted_time.to_db() if inbox_task.accepted_time else None,
                    working_time=inbox_task.working_time.to_db() if inbox_task.working_time else None,
                    completed_time=inbox_task.completed_time.to_db() if inbox_task.completed_time else None))
        inbox_task = inbox_task.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._inbox_task_event_table, inbox_task)
        return inbox_task

    def save(self, inbox_task: InboxTask) -> InboxTask:
        """Save an inbox task."""
        result = self._connection.execute(
            update(self._inbox_task_table)
            .where(self._inbox_task_table.c.ref_id == inbox_task.ref_id.as_int())
            .values(
                ref_id=inbox_task.ref_id.as_int() if inbox_task.ref_id != BAD_REF_ID else None,
                version=inbox_task.version,
                archived=inbox_task.archived,
                created_time=inbox_task.created_time.to_db(),
                last_modified_time=inbox_task.last_modified_time.to_db(),
                archived_time=inbox_task.archived_time.to_db() if inbox_task.archived_time else None,
                inbox_task_collection_ref_id=inbox_task.inbox_task_collection_ref_id.as_int(),
                source=str(inbox_task.source),
                big_plan_ref_id=inbox_task.big_plan_ref_id.as_int() if inbox_task.big_plan_ref_id else None,
                recurring_task_ref_id=
                inbox_task.recurring_task_ref_id.as_int() if inbox_task.recurring_task_ref_id else None,
                metric_ref_id=inbox_task.metric_ref_id.as_int() if inbox_task.metric_ref_id else None,
                person_ref_id=inbox_task.person_ref_id.as_int() if inbox_task.person_ref_id else None,
                name=str(inbox_task.name),
                status=str(inbox_task.status),
                eisen=str(inbox_task.eisen),
                difficulty=str(inbox_task.difficulty) if inbox_task.difficulty else None,
                actionable_date=inbox_task.actionable_date.to_db() if inbox_task.actionable_date else None,
                due_date=inbox_task.due_date.to_db() if inbox_task.due_date else None,
                recurring_timeline=inbox_task.recurring_timeline,
                recurring_type=str(inbox_task.recurring_type) if inbox_task.recurring_type else None,
                recurring_gen_right_now=
                inbox_task.recurring_gen_right_now.to_db() if inbox_task.recurring_gen_right_now else None,
                accepted_time=inbox_task.accepted_time.to_db() if inbox_task.accepted_time else None,
                working_time=inbox_task.working_time.to_db() if inbox_task.working_time else None,
                completed_time=inbox_task.completed_time.to_db() if inbox_task.completed_time else None))
        if result.rowcount == 0:
            raise InboxTaskNotFoundError(f"inbox task with id {inbox_task.ref_id} does not exist")
        upsert_events(self._connection, self._inbox_task_event_table, inbox_task)
        return inbox_task

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTask:
        """Retrieve an inbox task."""
        query_stmt = select(self._inbox_task_table).where(self._inbox_task_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._inbox_task_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise InboxTaskNotFoundError(f"inbox task with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_inbox_task_collection_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_sources: Optional[Iterable[InboxTaskSource]] = None,
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_person_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[InboxTask]:
        """Find all the inbox task."""
        query_stmt = select(self._inbox_task_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._inbox_task_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._inbox_task_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_inbox_task_collection_ref_ids:
            query_stmt = query_stmt.where(
                self._inbox_task_table.c.inbox_task_collection_ref_id.in_(
                    fi.as_int() for fi in filter_inbox_task_collection_ref_ids))
        if filter_sources:
            query_stmt = query_stmt.where(self._inbox_task_table.c.source.in_(str(s) for s in filter_sources))
        if filter_big_plan_ref_ids:
            query_stmt = \
                query_stmt\
                .where(self._inbox_task_table.c.big_plan_ref_id.in_(fi.as_int() for fi in filter_big_plan_ref_ids))
        if filter_recurring_task_ref_ids:
            query_stmt = query_stmt.where(
                self._inbox_task_table.c.recurring_task_ref_id.in_(fi.as_int() for fi in filter_recurring_task_ref_ids))
        if filter_metric_ref_ids:
            query_stmt = query_stmt.where(
                self._inbox_task_table.c.metric_ref_id.in_(fi.as_int() for fi in filter_metric_ref_ids))
        if filter_person_ref_ids:
            query_stmt = query_stmt.where(
                self._inbox_task_table.c.person_ref_id.in_(fi.as_int() for fi in filter_person_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> InboxTask:
        """Remove an inbox task."""
        query_stmt = select(self._inbox_task_table).where(self._inbox_task_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise InboxTaskNotFoundError(f"inbox task with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._inbox_task_table).where(self._inbox_task_table.c.ref_id == ref_id.as_int()))
        remove_events(self._connection, self._inbox_task_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> InboxTask:
        return InboxTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            inbox_task_collection_ref_id=EntityId.from_raw(str(row["inbox_task_collection_ref_id"])),
            source=InboxTaskSource.from_raw(row["source"]),
            big_plan_ref_id=EntityId.from_raw(str(row["big_plan_ref_id"])) if row["big_plan_ref_id"] else None,
            recurring_task_ref_id=
            EntityId.from_raw(str(row["recurring_task_ref_id"])) if row["recurring_task_ref_id"] else None,
            metric_ref_id=EntityId.from_raw(str(row["metric_ref_id"])) if row["metric_ref_id"] else None,
            person_ref_id=EntityId.from_raw(str(row["person_ref_id"])) if row["person_ref_id"] else None,
            name=InboxTaskName.from_raw(row["name"]),
            status=InboxTaskStatus.from_raw(row["status"]),
            eisen=Eisen.from_raw(row["eisen"]),
            difficulty=Difficulty.from_raw(row["difficulty"]) if row["difficulty"] else None,
            actionable_date=ADate.from_db(row["actionable_date"]) if row["actionable_date"] else None,
            due_date=ADate.from_db(row["due_date"]) if row["due_date"] else None,
            recurring_timeline=row["recurring_timeline"],
            recurring_type=RecurringTaskType.from_raw(row["recurring_type"]) if row["recurring_type"] else None,
            recurring_gen_right_now=
            Timestamp.from_db(row["recurring_gen_right_now"]) if row["recurring_gen_right_now"] else None,
            accepted_time=Timestamp.from_db(row["accepted_time"]) if row["accepted_time"] else None,
            working_time=Timestamp.from_db(row["working_time"]) if row["working_time"] else None,
            completed_time=Timestamp.from_db(row["completed_time"]) if row["completed_time"] else None)
