"""The SQLIte based user workspace links repository."""
from typing import Final

from jupiter.core.domain.user_workspace_link.infra.user_workspace_link_repository import (
    UserWorkspaceLinkNotFoundError,
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import build_event_table, upsert_events
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteUserWorkspaceLinkRepository(UserWorkspaceLinkRepository):
    """The SQLite based user workspace links repository."""

    _connection: Final[AsyncConnection]
    _user_workspace_link_table: Final[Table]
    _user_workspace_link_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._user_workspace_link_table = Table(
            "user_workspace_link",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "user_ref_id",
                Integer,
                ForeignKey("user.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column(
                "workspace_ref_id",
                Integer,
                ForeignKey("workspace.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            keep_existing=True,
        )
        self._user_workspace_link_event_table = build_event_table(
            self._user_workspace_link_table, metadata
        )

    async def create(self, entity: UserWorkspaceLink) -> UserWorkspaceLink:
        """Create a user workspace link."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._user_workspace_link_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                user_ref_id=entity.user_ref_id.as_int(),
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection, self._user_workspace_link_event_table, entity
        )
        return entity

    async def save(self, entity: UserWorkspaceLink) -> UserWorkspaceLink:
        """Save a user workspace link."""
        result = await self._connection.execute(
            update(self._user_workspace_link_table)
            .where(self._user_workspace_link_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                user_ref_id=entity.user_ref_id.as_int(),
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            )
        )
        if result.rowcount == 0:
            raise UserWorkspaceLinkNotFoundError(
                f"User workspace link with id {entity.ref_id} does not exist"
            )

        await upsert_events(
            self._connection, self._user_workspace_link_event_table, entity
        )
        return entity

    async def load_by_id(self, entity_id: EntityId) -> UserWorkspaceLink:
        """Retrieve a user workspace link by id."""
        query_stmt = select(self._user_workspace_link_table).where(
            self._user_workspace_link_table.c.ref_id == entity_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise UserWorkspaceLinkNotFoundError(
                f"User workspace link with id {entity_id} does not exist"
            )
        return self._row_to_entity(result)

    async def load_optional(self, entity_id: EntityId) -> UserWorkspaceLink | None:
        """Retrieve a user workspace link by id."""
        query_stmt = select(self._user_workspace_link_table).where(
            self._user_workspace_link_table.c.ref_id == entity_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def load_by_user(self, user_id: EntityId) -> UserWorkspaceLink:
        """Load the user workspace link for a particular user."""
        query_stmt = select(self._user_workspace_link_table).where(
            self._user_workspace_link_table.c.user_ref_id == user_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise UserWorkspaceLinkNotFoundError(
                f"User workspace link for user with id {user_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> UserWorkspaceLink:
        return UserWorkspaceLink(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            events=[],
            user_ref_id=EntityId.from_raw(str(row["user_ref_id"])),
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])),
        )
