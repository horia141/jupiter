"""The SQLite based search repository."""
from typing import Final, Iterable, List

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search_repository import SearchMatch, SearchRepository
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.repository import EntityNotFoundError
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
    text,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteSearchRepository(SearchRepository):
    """The SQLite based search repository."""

    _connection: Final[AsyncConnection]
    _search_index_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._search_index_table = Table(
            "search_index",
            metadata,
            Column(
                "workspace_ref_id",
                Integer,
                ForeignKey("workspace.ref_id"),
                nullable=False,
            ),
            Column("entity_tag", String, nullable=False),
            Column("parent_ref_id", Integer, nullable=False),
            Column("ref_id", Integer, nullable=False),
            Column("name", String, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            keep_existing=True,
        )

    async def create(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Create an entity in the index."""
        await self._connection.execute(
            insert(self._search_index_table).values(
                workspace_ref_id=workspace_ref_id.as_int(),
                entity_tag=str(NamedEntityTag.from_entity(entity)),
                parent_ref_id=entity.parent_ref_id.as_int(),
                ref_id=entity.ref_id.as_int(),
                name=str(entity.name),
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
            )
        )

    async def update(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Update an entity in the index."""
        result = await self._connection.execute(
            update(self._search_index_table)
            .where(
                self._search_index_table.c.workspace_ref_id == workspace_ref_id.as_int()
            )
            .where(
                self._search_index_table.c.entity_tag
                == str(NamedEntityTag.from_entity(entity))
            )
            .where(self._search_index_table.c.ref_id == entity.ref_id.as_int())
            .values(name=str(entity.name), archived=entity.archived)
        )
        if result.rowcount == 0:
            raise EntityNotFoundError(
                "The entity does not exist",
            )

    async def remove(
        self, workspace_ref_id: EntityId, entity: BranchEntity | LeafEntity
    ) -> None:
        """Remove an entity from the index."""
        await self._connection.execute(
            delete(self._search_index_table)
            .where(
                self._search_index_table.c.workspace_ref_id == workspace_ref_id.as_int()
            )
            .where(
                self._search_index_table.c.entity_tag
                == str(NamedEntityTag.from_entity(entity))
            )
            .where(self._search_index_table.c.ref_id == entity.ref_id.as_int())
        )

    async def drop(self) -> None:
        """Remove everything from the index."""
        await self._connection.execute(delete(self._search_index_table))

    async def search(
        self,
        workspace_ref_id: EntityId,
        query: str,
        limit: int,
        include_archived: bool,
        filter_entity_tags: Iterable[NamedEntityTag] | None,
    ) -> List[SearchMatch]:
        """Search for entities in the index."""
        query_stmt = (
            select(
                self._search_index_table.c.workspace_ref_id,
                self._search_index_table.c.entity_tag,
                self._search_index_table.c.parent_ref_id,
                self._search_index_table.c.ref_id,
                self._search_index_table.c.name,
                self._search_index_table.c.archived,
                self._search_index_table.c.created_time,
                self._search_index_table.c.last_modified_time,
                self._search_index_table.c.archived_time,
                text("highlight(search_index, 4, '[found]', '[/found]') as highlight"),
                text(
                    "snippet(search_index, 4, '[found]', '[/found]', '[nomatch]', 64) as snippet"
                ),
                text("rank"),
            )
            .where(
                self._search_index_table.c.workspace_ref_id == workspace_ref_id.as_int()
            )
            .where(self._search_index_table.c.name.match(query))
        )
        if not include_archived:
            query_stmt = query_stmt.where(
                self._search_index_table.c.archived.is_(False)
            )
        if filter_entity_tags is not None:
            query_stmt = query_stmt.where(
                self._search_index_table.c.entity_tag.in_(
                    str(f) for f in filter_entity_tags
                )
            )
        query_stmt = query_stmt.limit(limit)
        query_stmt = query_stmt.order_by(text("rank"))
        results = await self._connection.execute(query_stmt)
        return [self._row_to_match(row) for row in results]

    @staticmethod
    def _row_to_match(row: RowType) -> SearchMatch:
        return SearchMatch(
            entity_tag=NamedEntityTag.from_raw(row["entity_tag"]),
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            parent_ref_id=EntityId.from_raw(str(row["parent_ref_id"])),
            name=EntityName.from_raw(row["name"]),
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            match_highlight=row["highlight"],
            match_snippet=row["snippet"],
            search_rank=row["rank"],
        )
