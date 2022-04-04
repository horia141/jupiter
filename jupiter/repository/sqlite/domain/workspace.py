"""The SQLite based Workspace repository."""
from typing import Final, Optional

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
)
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import OperationalError

from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
    WorkspaceNotFoundError,
    WorkspaceAlreadyExistsError,
)
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import build_event_table, upsert_events


class SqliteWorkspaceRepository(WorkspaceRepository):
    """A repository for Workspaces."""

    _connection: Final[Connection]
    _workspace_table: Final[Table]
    _workspace_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._workspace_table = Table(
            "workspace",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column("name", String(100), nullable=False),
            Column("timezone", String(100), nullable=False),
            Column("default_project_ref_id", Integer, nullable=True),
            keep_existing=True,
        )
        self._workspace_event_table = build_event_table(self._workspace_table, metadata)

    def create(self, entity: Workspace) -> Workspace:
        """Create a workspace."""
        try:
            entity = self.load()
            raise WorkspaceAlreadyExistsError("Workspace already exists")
        except WorkspaceNotFoundError:
            pass
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._workspace_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                name=str(entity.name),
                timezone=str(entity.timezone),
                default_project_ref_id=entity.default_project_ref_id.as_int()
                if entity.default_project_ref_id is not BAD_REF_ID
                else None
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._workspace_event_table, entity)
        return entity

    def save(self, entity: Workspace) -> Workspace:
        """Save the workspace."""
        result = self._connection.execute(
            update(self._workspace_table)
            .where(self._workspace_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                name=str(entity.name),
                timezone=str(entity.timezone),
                default_project_ref_id=entity.default_project_ref_id.as_int()
                if entity.default_project_ref_id
                else None,
            )
        )
        if result.rowcount == 0:
            raise WorkspaceNotFoundError("The workspace does not exist")
        upsert_events(self._connection, self._workspace_event_table, entity)
        return entity

    def load(self) -> Workspace:
        """Load the workspace."""
        query_stmt = select(self._workspace_table)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise WorkspaceNotFoundError("Missing workspace")
        return self._row_to_entity(result)

    def load_optional(self) -> Optional[Workspace]:
        """Load the workspace."""
        query_stmt = select(self._workspace_table)
        try:
            result = self._connection.execute(query_stmt).first()
            if result is None:
                return None
            return self._row_to_entity(result)
        except OperationalError as err:
            if str(err).find("no such table: workspace") >= 0:
                return None
            raise

    @staticmethod
    def _row_to_entity(row: Result) -> Workspace:
        return Workspace(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=WorkspaceName.from_raw(row["name"]),
            timezone=Timezone.from_raw(row["timezone"]),
            default_project_ref_id=EntityId.from_raw(
                str(row["default_project_ref_id"])
            ),
        )
