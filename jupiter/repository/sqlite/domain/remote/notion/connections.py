"""The SQLite based Notion connection repository."""
from typing import Final

from sqlalchemy import (
    Table,
    MetaData,
    Integer,
    Boolean,
    DateTime,
    Column,
    String,
    insert,
    update,
    select,
    ForeignKey,
)
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError

from jupiter.domain.remote.notion.connection_repository import (
    NotionConnectionRepository,
    NotionConnectionAlreadyExistsError,
    NotionConnectionNotFoundError,
)
from jupiter.domain.remote.notion.connection import NotionConnection
from jupiter.domain.remote.notion.space_id import NotionSpaceId
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events


class SqliteNotionConnectionRepository(NotionConnectionRepository):
    """The SQLite based Notion connection repository."""

    _connection: Final[Connection]
    _notion_connection_table: Final[Table]
    _notion_connection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_connection_table = Table(
            "notion_connection",
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
                ForeignKey("workspace.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column("space_id", String, nullable=False),
            Column("token", String, nullable=False),
            keep_existing=True,
        )
        self._notion_connection_event_table = build_event_table(
            self._notion_connection_table, metadata
        )

    def create(self, entity: NotionConnection) -> NotionConnection:
        """Create a Notion connection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = self._connection.execute(
                insert(self._notion_connection_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    workspace_ref_id=entity.workspace_ref_id.as_int(),
                    space_id=str(entity.space_id),
                    token=str(entity.token),
                )
            )
        except IntegrityError as err:
            raise NotionConnectionAlreadyExistsError(
                f"Notion connection for workspace {entity.workspace_ref_id} already exists"
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._notion_connection_event_table, entity)
        return entity

    def save(self, entity: NotionConnection) -> NotionConnection:
        """Save a Notion connection."""
        result = self._connection.execute(
            update(self._notion_connection_table)
            .where(self._notion_connection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                space_id=str(entity.space_id),
                token=str(entity.token),
            )
        )
        if result.rowcount == 0:
            raise NotionConnectionNotFoundError(
                f"The Notion connection does not exist for workspace {entity.workspace_ref_id}"
            )
        upsert_events(self._connection, self._notion_connection_event_table, entity)
        return entity

    def load_by_parent(self, parent_ref_id: EntityId) -> NotionConnection:
        """Load the Notion connection for the workspace."""
        query_stmt = select(self._notion_connection_table).where(
            self._notion_connection_table.c.workspace_ref_id == parent_ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise NotionConnectionNotFoundError(
                f"Notion connection for workspace {parent_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> NotionConnection:
        return NotionConnection(
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
            space_id=NotionSpaceId.from_raw(row["space_id"]),
            token=NotionToken.from_raw(row["token"]),
        )
