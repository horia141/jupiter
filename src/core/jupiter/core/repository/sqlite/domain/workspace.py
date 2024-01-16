"""The SQLite based Workspace repository."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
    WorkspaceRepository,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.realm import RealmCodecRegistry
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
            not_found_err_cls=WorkspaceNotFoundError,
        )
