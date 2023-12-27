"""The SQLIte based user workspace links repository."""

from jupiter.core.domain.user_workspace_link.infra.user_workspace_link_repository import (
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.repository import SqliteRootEntityRepository
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteUserWorkspaceLinkRepository(
    SqliteRootEntityRepository[UserWorkspaceLink], UserWorkspaceLinkRepository
):
    """The SQLite based user workspace links repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    async def load_by_user(self, user_id: EntityId) -> UserWorkspaceLink:
        """Load the user workspace link for a particular user."""
        query_stmt = select(self._table).where(
            self._table.c.user_ref_id == user_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"User workspace link for user with id {user_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _entity_to_row(entity: UserWorkspaceLink) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "user_ref_id": entity.user_ref_id.as_int(),
            "workspace_ref_id": entity.workspace_ref_id.as_int(),
        }

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
