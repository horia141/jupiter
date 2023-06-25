"""The SQLite based projects repository."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionNotFoundError,
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import (
    ProjectNotFoundError,
    ProjectRepository,
)
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
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
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteProjectCollectionRepository(ProjectCollectionRepository):
    """The project collection repository."""

    _connection: Final[AsyncConnection]
    _project_collection_table: Final[Table]
    _project_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._project_collection_table = Table(
            "project_collection",
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
            keep_existing=True,
        )
        self._project_collection_event_table = build_event_table(
            self._project_collection_table,
            metadata,
        )

    async def create(self, entity: ProjectCollection) -> ProjectCollection:
        """Create a project collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._project_collection_table).values(
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
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._project_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: ProjectCollection) -> ProjectCollection:
        """Save a big project collection."""
        result = await self._connection.execute(
            update(self._project_collection_table)
            .where(self._project_collection_table.c.ref_id == entity.ref_id.as_int())
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
            raise ProjectCollectionNotFoundError(
                "The project collection does not exist",
            )
        await upsert_events(
            self._connection,
            self._project_collection_event_table,
            entity,
        )
        return entity

    async def load_by_parent(self, parent_ref_id: EntityId) -> ProjectCollection:
        """Load a project collection for a given project."""
        query_stmt = select(self._project_collection_table).where(
            self._project_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ProjectCollectionNotFoundError(
                f"Big plan collection for project {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> ProjectCollection:
        return ProjectCollection(
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


class SqliteProjectRepository(ProjectRepository):
    """A repository for projects."""

    _connection: Final[AsyncConnection]
    _project_table: Final[Table]
    _project_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._project_table = Table(
            "project",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "project_collection_ref_id",
                Integer,
                ForeignKey("project_collection.ref_id"),
                nullable=False,
            ),
            Column("name", String(100), nullable=False),
            keep_existing=True,
        )
        self._project_event_table = build_event_table(self._project_table, metadata)

    async def create(self, entity: Project) -> Project:
        """Create a project."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._project_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                project_collection_ref_id=entity.project_collection_ref_id.as_int(),
                name=str(entity.name),
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._project_event_table, entity)
        return entity

    async def save(self, entity: Project) -> Project:
        """Save a project."""
        result = await self._connection.execute(
            update(self._project_table)
            .where(self._project_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                project_collection_ref_id=entity.project_collection_ref_id.as_int(),
                name=str(entity.name),
            ),
        )
        if result.rowcount == 0:
            raise ProjectNotFoundError("The project does not exist")
        await upsert_events(self._connection, self._project_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Project:
        """Retrieve a project."""
        query_stmt = select(self._project_table).where(
            self._project_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._project_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ProjectNotFoundError(f"Project with id {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Project]:
        """Find all projects."""
        return await self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids,
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Project]:
        """Find all projects."""
        query_stmt = select(self._project_table).where(
            self._project_table.c.project_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._project_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._project_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Project:
        """Remove a project."""
        query_stmt = select(self._project_table).where(
            self._project_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise ProjectNotFoundError(f"Project with id {ref_id} does not exist")
        await self._connection.execute(
            delete(self._project_table).where(
                self._project_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._project_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Project:
        return Project(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            project_collection_ref_id=EntityId.from_raw(
                str(row["project_collection_ref_id"]),
            ),
            name=ProjectName.from_raw(row["name"]),
        )
