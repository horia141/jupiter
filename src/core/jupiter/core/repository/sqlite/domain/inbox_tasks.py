"""The SQLite repository for inbox tasks."""
from typing import Iterable, List, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.core.domain.inbox_tasks.infra.inbox_task_repository import (
    InboxTaskRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.realm import RealmCodecRegistry
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
    Unicode,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteInboxTaskCollectionRepository(
    SqliteTrunkEntityRepository[InboxTaskCollection], InboxTaskCollectionRepository
):
    """The inbox task collection repository."""

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
                "inbox_task_collection",
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
                    index=True,
                    unique=True,
                    nullable=False,
                ),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: InboxTaskCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
        }

    def _row_to_entity(self, row: RowType) -> InboxTaskCollection:
        return InboxTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace=ParentLink(EntityId.from_raw(str(row["workspace_ref_id"]))),
        )


class SqliteInboxTaskRepository(
    SqliteLeafEntityRepository[InboxTask], InboxTaskRepository
):
    """The inbox task repository."""

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
                "inbox_task",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "inbox_task_collection_ref_id",
                    Integer,
                    ForeignKey("inbox_task_collection.ref_id"),
                    nullable=False,
                ),
                Column("source", String(16), nullable=False),
                Column(
                    "project_ref_id",
                    Integer,
                    ForeignKey("project.ref_id"),
                    nullable=False,
                    index=True,
                ),
                Column(
                    "big_plan_ref_id",
                    Integer,
                    ForeignKey("big_plan.ref_id"),
                    nullable=True,
                ),
                Column(
                    "habit_ref_id", Integer, ForeignKey("habit.ref_id"), nullable=True
                ),
                Column(
                    "chore_ref_id", Integer, ForeignKey("chore.ref_id"), nullable=True
                ),
                Column(
                    "journal_ref_id",
                    Integer,
                    ForeignKey("journal.ref_id"),
                    nullable=True,
                ),
                Column(
                    "metric_ref_id",
                    Integer,
                    ForeignKey("metric.ref_id"),
                    nullable=True,
                ),
                Column(
                    "person_ref_id",
                    Integer,
                    ForeignKey("person.ref_id"),
                    nullable=True,
                ),
                Column(
                    "slack_task_ref_id",
                    Integer,
                    ForeignKey("slack_task.ref_id"),
                    nullable=True,
                ),
                Column(
                    "email_task_ref_id",
                    Integer,
                    ForeignKey("email_task.ref_id"),
                    nullable=True,
                ),
                Column("name", Unicode(), nullable=False),
                Column("status", String(16), nullable=False),
                Column("eisen", String(20), nullable=False),
                Column("difficulty", String(10), nullable=True),
                Column("actionable_date", DateTime, nullable=True),
                Column("due_date", DateTime, nullable=True),
                Column("notes", Unicode(), nullable=True),
                Column("recurring_timeline", String, nullable=True),
                Column("recurring_repeat_index", Integer, nullable=True),
                Column("recurring_gen_right_now", DateTime, nullable=True),
                Column("accepted_time", DateTime, nullable=True),
                Column("working_time", DateTime, nullable=True),
                Column("completed_time", DateTime, nullable=True),
                keep_existing=True,
            ),
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_sources: Optional[Iterable[InboxTaskSource]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_habit_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_chore_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_journal_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_person_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_slack_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_email_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_last_modified_time_start: Optional[ADate] = None,
        filter_last_modified_time_end: Optional[ADate] = None,
    ) -> List[InboxTask]:
        """Find all the inbox task."""
        query_stmt = select(self._table).where(
            self._table.c.inbox_task_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_sources is not None:
            query_stmt = query_stmt.where(
                self._table.c.source.in_(s.value for s in filter_sources),
            )
        if filter_project_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.project_ref_id.in_(
                    fi.as_int() for fi in filter_project_ref_ids
                ),
            )
        if filter_habit_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.habit_ref_id.in_(
                    fi.as_int() for fi in filter_habit_ref_ids
                ),
            )
        if filter_chore_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.chore_ref_id.in_(
                    fi.as_int() for fi in filter_chore_ref_ids
                ),
            )
        if filter_big_plan_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.big_plan_ref_id.in_(
                    fi.as_int() for fi in filter_big_plan_ref_ids
                ),
            )
        if filter_journal_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.journal_ref_id.in_(
                    fi.as_int() for fi in filter_journal_ref_ids
                ),
            )
        if filter_metric_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.metric_ref_id.in_(
                    fi.as_int() for fi in filter_metric_ref_ids
                ),
            )
        if filter_person_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.person_ref_id.in_(
                    fi.as_int() for fi in filter_person_ref_ids
                ),
            )
        if filter_slack_task_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.slack_task_ref_id.in_(
                    fi.as_int() for fi in filter_slack_task_ref_ids
                ),
            )
        if filter_email_task_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.email_task_ref_id.in_(
                    fi.as_int() for fi in filter_email_task_ref_ids
                ),
            )
        if filter_last_modified_time_start is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                >= filter_last_modified_time_start.to_db(),
            )
        if filter_last_modified_time_end is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                < filter_last_modified_time_end.to_db(),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def _entity_to_row(self, entity: InboxTask) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "inbox_task_collection_ref_id": entity.inbox_task_collection.as_int(),
            "source": str(entity.source),
            "project_ref_id": entity.project_ref_id.as_int(),
            "habit_ref_id": entity.habit_ref_id.as_int()
            if entity.habit_ref_id
            else None,
            "chore_ref_id": entity.chore_ref_id.as_int()
            if entity.chore_ref_id
            else None,
            "big_plan_ref_id": entity.big_plan_ref_id.as_int()
            if entity.big_plan_ref_id
            else None,
            "journal_ref_id": entity.journal_ref_id.as_int()
            if entity.journal_ref_id
            else None,
            "metric_ref_id": entity.metric_ref_id.as_int()
            if entity.metric_ref_id
            else None,
            "person_ref_id": entity.person_ref_id.as_int()
            if entity.person_ref_id
            else None,
            "slack_task_ref_id": entity.slack_task_ref_id.as_int()
            if entity.slack_task_ref_id
            else None,
            "email_task_ref_id": entity.email_task_ref_id.as_int()
            if entity.email_task_ref_id
            else None,
            "name": str(entity.name),
            "status": str(entity.status),
            "eisen": str(entity.eisen),
            "difficulty": str(entity.difficulty) if entity.difficulty else None,
            "actionable_date": entity.actionable_date.to_db()
            if entity.actionable_date
            else None,
            "due_date": entity.due_date.to_db() if entity.due_date else None,
            "notes": entity.notes,
            "recurring_timeline": entity.recurring_timeline,
            "recurring_repeat_index": entity.recurring_repeat_index,
            "recurring_gen_right_now": entity.recurring_gen_right_now.to_db()
            if entity.recurring_gen_right_now
            else None,
            "accepted_time": entity.accepted_time.to_db()
            if entity.accepted_time
            else None,
            "working_time": entity.working_time.to_db()
            if entity.working_time
            else None,
            "completed_time": entity.completed_time.to_db()
            if entity.completed_time
            else None,
        }

    def _row_to_entity(self, row: RowType) -> InboxTask:
        return InboxTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            inbox_task_collection=ParentLink(
                EntityId.from_raw(
                    str(row["inbox_task_collection_ref_id"]),
                )
            ),
            source=InboxTaskSource.from_raw(row["source"]),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            habit_ref_id=EntityId.from_raw(str(row["habit_ref_id"]))
            if row["habit_ref_id"]
            else None,
            chore_ref_id=EntityId.from_raw(str(row["chore_ref_id"]))
            if row["chore_ref_id"]
            else None,
            big_plan_ref_id=EntityId.from_raw(str(row["big_plan_ref_id"]))
            if row["big_plan_ref_id"]
            else None,
            journal_ref_id=EntityId.from_raw(str(row["journal_ref_id"]))
            if row["journal_ref_id"]
            else None,
            metric_ref_id=EntityId.from_raw(str(row["metric_ref_id"]))
            if row["metric_ref_id"]
            else None,
            person_ref_id=EntityId.from_raw(str(row["person_ref_id"]))
            if row["person_ref_id"]
            else None,
            slack_task_ref_id=EntityId.from_raw(str(row["slack_task_ref_id"]))
            if row["slack_task_ref_id"]
            else None,
            email_task_ref_id=EntityId.from_raw(str(row["email_task_ref_id"]))
            if row["email_task_ref_id"]
            else None,
            name=InboxTaskName.from_raw(row["name"]),
            status=InboxTaskStatus.from_raw(row["status"]),
            eisen=Eisen.from_raw(row["eisen"]),
            difficulty=Difficulty.from_raw(row["difficulty"])
            if row["difficulty"]
            else None,
            actionable_date=ADate.from_db(row["actionable_date"])
            if row["actionable_date"]
            else None,
            due_date=ADate.from_db(row["due_date"]) if row["due_date"] else None,
            notes=row["notes"],
            recurring_timeline=row["recurring_timeline"],
            recurring_repeat_index=row["recurring_repeat_index"],
            recurring_gen_right_now=Timestamp.from_db(row["recurring_gen_right_now"])
            if row["recurring_gen_right_now"]
            else None,
            accepted_time=Timestamp.from_db(row["accepted_time"])
            if row["accepted_time"]
            else None,
            working_time=Timestamp.from_db(row["working_time"])
            if row["working_time"]
            else None,
            completed_time=Timestamp.from_db(row["completed_time"])
            if row["completed_time"]
            else None,
        )
