"""The SQLite based Workspace repository."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.repository import SqliteRootEntityRepository
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
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteWorkspaceRepository(
    SqliteRootEntityRepository[Workspace], WorkspaceRepository
):
    """A repository for Workspaces."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    @staticmethod
    def _entity_to_row(entity: Workspace) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "name": str(entity.name),
            "default_project_ref_id": entity.default_project_ref_id.as_int(),
            "feature_flags": {f.value: v for f, v in entity.feature_flags.items()},
        }

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
            feature_flags={
                WorkspaceFeature(f): v for f, v in row["feature_flags"].items()
            },
        )
