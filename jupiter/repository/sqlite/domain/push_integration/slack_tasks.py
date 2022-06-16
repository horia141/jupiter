"""The Slack tasks repositories."""
from typing import Final, Optional, Iterable, List

from sqlalchemy import (
    insert,
    MetaData,
    Table,
    Column,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    update,
    select,
    String,
    delete,
)
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError

from jupiter.domain.push_integrations.push_generation_extra_info import (
    PushGenerationExtraInfo,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
    SlackTaskCollectionAlreadyExistsError,
    SlackTaskCollectionNotFoundError,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
    SlackTaskNotFoundError,
)
from jupiter.domain.push_integrations.slack.slack_channel_name import SlackChannelName
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import (
    upsert_events,
    build_event_table,
    remove_events,
)


class SqliteSlackTaskCollectionRepository(SlackTaskCollectionRepository):
    """The slack task collection repository."""

    _connection: Final[Connection]
    _slack_task_collection_table: Final[Table]
    _slack_task_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._slack_task_collection_table = Table(
            "slack_task_collection",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "push_integration_group_ref_id",
                Integer,
                ForeignKey("push_integration_group_ref_id.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column(
                "generation_project_ref_id",
                Integer,
                ForeignKey("project.ref_id"),
                nullable=False,
            ),
            keep_existing=True,
        )
        self._slack_task_collection_event_table = build_event_table(
            self._slack_task_collection_table, metadata
        )

    def create(self, entity: SlackTaskCollection) -> SlackTaskCollection:
        """Create a slack task collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = self._connection.execute(
                insert(self._slack_task_collection_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    push_integration_group_ref_id=entity.push_integration_group_ref_id.as_int(),
                    generation_project_ref_id=entity.generation_project_ref_id.as_int(),
                )
            )
        except IntegrityError as err:
            raise SlackTaskCollectionAlreadyExistsError(
                f"SlackTask collection for push integration group {entity.push_integration_group_ref_id} "
                + "already exists"
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._slack_task_collection_event_table, entity)
        return entity

    def save(self, entity: SlackTaskCollection) -> SlackTaskCollection:
        """Save a slack task collection."""
        result = self._connection.execute(
            update(self._slack_task_collection_table)
            .where(self._slack_task_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                push_integration_group_ref_id=entity.push_integration_group_ref_id.as_int(),
                generation_project_ref_id=entity.generation_project_ref_id.as_int(),
            )
        )
        if result.rowcount == 0:
            raise SlackTaskCollectionNotFoundError(
                "The slack task collection does not exist"
            )
        upsert_events(self._connection, self._slack_task_collection_event_table, entity)
        return entity

    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> SlackTaskCollection:
        """Retrieve a slack task collection."""
        query_stmt = select(self._slack_task_collection_table).where(
            self._slack_task_collection_table.c.ref_id == ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._slack_task_collection_table.c.archived.is_(False)
            )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SlackTaskCollectionNotFoundError(
                f"SlackTask collection with id {ref_id} does not exist"
            )
        return self._row_to_entity(result)

    def load_by_parent(self, parent_ref_id: EntityId) -> SlackTaskCollection:
        """Retrieve a slack task collection for a project."""
        query_stmt = select(self._slack_task_collection_table).where(
            self._slack_task_collection_table.c.push_integration_group_ref_id
            == parent_ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SlackTaskCollectionNotFoundError(
                f"SlackTask collection for push integration group {parent_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SlackTaskCollection:
        return SlackTaskCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            push_integration_group_ref_id=EntityId.from_raw(
                str(row["push_integration_group_ref_id"])
            ),
            generation_project_ref_id=EntityId.from_raw(
                str(row["generation_project_ref_id"])
            ),
        )


class SqliteSlackTaskRepository(SlackTaskRepository):
    """The slack task repository."""

    _connection: Final[Connection]
    _slack_task_table: Final[Table]
    _slack_task_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._slack_task_table = Table(
            "slack_task",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "slack_task_collection_ref_id",
                Integer,
                ForeignKey("slack_task_collection.ref_id"),
                nullable=False,
            ),
            Column("user", String(), nullable=False),
            Column("channel", String(), nullable=True),
            Column("message", String(), nullable=False),
            Column("generation_extra_info", String(), nullable=False),
            Column("has_generated_task", Boolean, nullable=False),
            keep_existing=True,
        )
        self._slack_task_event_table = build_event_table(
            self._slack_task_table, metadata
        )

    def create(self, entity: SlackTask) -> SlackTask:
        """Create the slack task."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._slack_task_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                slack_task_collection_ref_id=entity.slack_task_collection_ref_id.as_int(),
                user=str(entity.user),
                channel=str(entity.channel) if entity.channel else None,
                message=entity.message,
                generation_extra_info=entity.generation_extra_info.to_db(),
                has_generated_task=entity.has_generated_task,
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._slack_task_event_table, entity)
        return entity

    def save(self, entity: SlackTask) -> SlackTask:
        """Save the slack task."""
        result = self._connection.execute(
            update(self._slack_task_table)
            .where(self._slack_task_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                slack_task_collection_ref_id=entity.slack_task_collection_ref_id.as_int(),
                user=str(entity.user),
                channel=str(entity.channel) if entity.channel else None,
                message=entity.message,
                generation_extra_info=entity.generation_extra_info.to_db(),
                has_generated_task=entity.has_generated_task,
            )
        )
        if result.rowcount == 0:
            raise SlackTaskNotFoundError(
                f"Slack task with id {entity.ref_id} does not exist"
            )
        upsert_events(self._connection, self._slack_task_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SlackTask:
        """Retrieve the slack task."""
        query_stmt = select(self._slack_task_table).where(
            self._slack_task_table.c.ref_id == ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._slack_task_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SlackTaskNotFoundError(f"Big plan with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[SlackTask]:
        """Find all the slack tasks."""
        query_stmt = select(self._slack_task_table).where(
            self._slack_task_table.c.slack_task_collection_ref_id
            == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._slack_task_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._slack_task_table.c.ref_id.in_(
                    fi.as_int() for fi in filter_ref_ids
                )
            )
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> SlackTask:
        """Remove a bit plan."""
        query_stmt = select(self._slack_task_table).where(
            self._slack_task_table.c.ref_id == ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise SlackTaskNotFoundError(f"Big plan with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._slack_task_table).where(
                self._slack_task_table.c.ref_id == ref_id.as_int()
            )
        )
        remove_events(self._connection, self._slack_task_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> SlackTask:
        return SlackTask(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            slack_task_collection_ref_id=EntityId.from_raw(
                str(row["slack_task_collection_ref_id"])
            ),
            user=SlackUserName.from_raw(row["user"]),
            channel=SlackChannelName.from_raw(row["channel"])
            if row["channel"]
            else None,
            message=row["message"],
            generation_extra_info=PushGenerationExtraInfo.from_db(
                row["generation_extra_info"]
            ),
            has_generated_task=row["has_generated_task"],
        )
