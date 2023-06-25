"""The push integration group repository SQLite implementation."""
from typing import Final

from jupiter.core.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupAlreadyExistsError,
    PushIntegrationGroupNotFoundError,
    PushIntegrationGroupRepository,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqlitePushIntegrationGroupRepository(PushIntegrationGroupRepository):
    """The push integration group repository SQLite implementation."""

    _connection: Final[AsyncConnection]
    _push_integration_group_table: Final[Table]
    _push_integration_group_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._push_integration_group_table = Table(
            "push_integration_group",
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
                unique=True,
                index=True,
                nullable=False,
            ),
            keep_existing=True,
        )
        self._push_integration_group_event_table = build_event_table(
            self._push_integration_group_table,
            metadata,
        )

    async def create(self, entity: PushIntegrationGroup) -> PushIntegrationGroup:
        """Create a push integration group."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._push_integration_group_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    workspace_ref_id=entity.workspace_ref_id.as_int(),
                ),
            )
        except IntegrityError as err:
            raise PushIntegrationGroupAlreadyExistsError(
                f"Push integration group for workspace {entity.workspace_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._push_integration_group_event_table,
            entity,
        )
        return entity

    async def save(self, entity: PushIntegrationGroup) -> PushIntegrationGroup:
        """Save a push integration group."""
        result = await self._connection.execute(
            update(self._push_integration_group_table)
            .where(
                self._push_integration_group_table.c.ref_id == entity.ref_id.as_int(),
            )
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise PushIntegrationGroupNotFoundError(
                "The push integration group does not exist",
            )
        await upsert_events(
            self._connection,
            self._push_integration_group_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> PushIntegrationGroup:
        """Retrieve a push integration group."""
        query_stmt = select(self._push_integration_group_table).where(
            self._push_integration_group_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._push_integration_group_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise PushIntegrationGroupNotFoundError(
                f"Push integration group with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> PushIntegrationGroup:
        """Retrieve a push integration group for a project."""
        query_stmt = select(self._push_integration_group_table).where(
            self._push_integration_group_table.c.workspace_ref_id
            == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise PushIntegrationGroupNotFoundError(
                f"Push integration group for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> PushIntegrationGroup:
        return PushIntegrationGroup(
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
        )
