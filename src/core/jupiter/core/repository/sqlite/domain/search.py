"""The SQLite based search repository."""
from typing import Final, Iterable, List

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.search_repository import SearchMatch, SearchRepository
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
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
            Column("ref_id", Integer, nullable=False),
            Column("name", String, nullable=False),
            Column("archived", Boolean, nullable=False),
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
                ref_id=entity.ref_id.as_int(),
                name=str(entity.name),
                archived=entity.archived,
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
            select(self._search_index_table)
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
            name=EntityName.from_raw(row["name"]),
            archived=row["archived"],
            match_highlight="",
            match_snippet="",
            search_rank=10.0,
        )
