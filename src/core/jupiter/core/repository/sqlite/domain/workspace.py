"""The SQLite based Workspace repository."""
from typing import Final, Optional

from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
    WorkspaceRepository,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import build_event_table, upsert_events
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    insert,
    select,
    update,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteWorkspaceRepository(WorkspaceRepository):
    """A repository for Workspaces."""

    _connection: Final[AsyncConnection]
    _workspace_table: Final[Table]
    _workspace_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
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
            Column("default_project_ref_id", Integer, nullable=True),
            Column("feature_flags", JSON, nullable=False),
            keep_existing=True,
        )
        self._workspace_event_table = build_event_table(self._workspace_table, metadata)

    async def create(self, entity: Workspace) -> Workspace:
        """Create a workspace."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
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
                default_project_ref_id=entity.default_project_ref_id.as_int(),
                feature_flags=entity.feature_flags,
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._workspace_event_table, entity)
        return entity

    async def save(self, entity: Workspace) -> Workspace:
        """Save the workspace."""
        result = await self._connection.execute(
            update(self._workspace_table)
            .where(self._workspace_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                name=str(entity.name),
                default_project_ref_id=entity.default_project_ref_id.as_int(),
                feature_flags=entity.feature_flags,
            ),
        )
        if result.rowcount == 0:
            raise WorkspaceNotFoundError(
                f"The workspace with id {entity.ref_id} does not exist"
            )
        await upsert_events(self._connection, self._workspace_event_table, entity)
        return entity

    async def load_by_id(self, entity_id: EntityId) -> Workspace:
        """Load the workspace."""
        query_stmt = select(self._workspace_table).where(
            self._workspace_table.c.ref_id == entity_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise WorkspaceNotFoundError(
                f"The workspace with id {entity_id} does not exist"
            )
        return self._row_to_entity(result)

    async def load_optional(self, entity_id: EntityId) -> Optional[Workspace]:
        """Load the workspace."""
        query_stmt = select(self._workspace_table).where(
            self._workspace_table.c.ref_id == entity_id.as_int(),
        )
        try:
            result = (await self._connection.execute(query_stmt)).first()
            if result is None:
                return None
            return self._row_to_entity(result)
        except OperationalError as err:
            if str(err).find("no such table: workspace") >= 0:
                return None
            raise

    @staticmethod
    def _row_to_entity(row: RowType) -> Workspace:
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
            default_project_ref_id=EntityId.from_raw(
                str(row["default_project_ref_id"]),
            ),
            feature_flags=row["feature_flags"],
        )
