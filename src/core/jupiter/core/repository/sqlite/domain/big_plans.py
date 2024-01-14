"""The SQLite big plans repository."""
from typing import Iterable, List, Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import (
    BigPlanRepository,
)
from jupiter.core.domain.core.adate import ADate
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


class SqliteBigPlanCollectionRepository(
    SqliteTrunkEntityRepository[BigPlanCollection], BigPlanCollectionRepository
):
    """The big plan collection repository."""

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
                "big_plan_collection",
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
            ),
        )

    def _entity_to_row(self, entity: BigPlanCollection) -> RowType:
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

    def _row_to_entity(self, row: RowType) -> BigPlanCollection:
        return BigPlanCollection(
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


class SqliteBigPlanRepository(SqliteLeafEntityRepository[BigPlan], BigPlanRepository):
    """The big plan repository."""

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
                "big_plan",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "big_plan_collection_ref_id",
                    Integer,
                    ForeignKey("big_plan_collection.ref_id"),
                    nullable=False,
                ),
                Column(
                    "project_ref_id",
                    Integer,
                    ForeignKey("project.ref_id"),
                    nullable=False,
                    index=True,
                ),
                Column("name", Unicode(), nullable=False),
                Column("status", String(16), nullable=False),
                Column("actionable_date", DateTime, nullable=True),
                Column("due_date", DateTime, nullable=True),
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
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[BigPlan]:
        """Find all the big plans."""
        query_stmt = select(self._table).where(
            self._table.c.big_plan_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_project_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.project_ref_id.in_(
                    fi.as_int() for fi in filter_project_ref_ids
                ),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def _entity_to_row(self, entity: BigPlan) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "big_plan_collection_ref_id": entity.big_plan_collection.as_int(),
            "project_ref_id": entity.project_ref_id.as_int(),
            "name": str(entity.name),
            "status": str(entity.status),
            "actionable_date": entity.actionable_date.to_db()
            if entity.actionable_date
            else None,
            "due_date": entity.due_date.to_db() if entity.due_date else None,
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

    def _row_to_entity(self, row: RowType) -> BigPlan:
        return BigPlan(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            big_plan_collection=ParentLink(
                EntityId.from_raw(
                    str(row["big_plan_collection_ref_id"]),
                )
            ),
            project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            name=BigPlanName.from_raw(row["name"]),
            status=BigPlanStatus.from_raw(row["status"]),
            actionable_date=ADate.from_db(row["actionable_date"])
            if row["actionable_date"]
            else None,
            due_date=ADate.from_db(row["due_date"]) if row["due_date"] else None,
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
