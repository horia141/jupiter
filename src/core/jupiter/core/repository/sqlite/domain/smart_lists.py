"""The SQLite based smart lists repository."""
from typing import Iterable, List, Optional

from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.url import URL
from jupiter.core.domain.smart_lists.infra.smart_list_collection_repository import (
    SmartListCollectionRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_item_repository import (
    SmartListItemRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_repository import (
    SmartListRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_tag_repository import (
    SmartListTagRepository,
)
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteBranchEntityRepository,
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteSmartListCollectionRepository(
    SqliteTrunkEntityRepository[SmartListCollection], SmartListCollectionRepository
):
    """The smart list collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "smart_list_collection",
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

    def _entity_to_row(self, entity: SmartListCollection) -> RowType:
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

    def _row_to_entity(self, row: RowType) -> SmartListCollection:
        return SmartListCollection(
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


class SqliteSmartListRepository(
    SqliteBranchEntityRepository[SmartList], SmartListRepository
):
    """A repository for lists."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "smart_list",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "smart_list_collection_ref_id",
                    Integer,
                    ForeignKey("smart_list_collection.ref_id"),
                    nullable=False,
                ),
                Column("name", String(100), nullable=False),
                Column("icon", String(1), nullable=True),
                keep_existing=True,
            ),
        )

    def _entity_to_row(self, entity: SmartList) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "smart_list_collection_ref_id": entity.smart_list_collection.as_int(),
            "name": str(entity.name),
            "icon": entity.icon.to_safe() if entity.icon else None,
        }

    def _row_to_entity(self, row: RowType) -> SmartList:
        return SmartList(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            smart_list_collection=ParentLink(
                EntityId.from_raw(
                    str(row["smart_list_collection_ref_id"]),
                )
            ),
            name=SmartListName.from_raw(row["name"]),
            icon=EntityIcon.from_safe(row["icon"]) if row["icon"] else None,
        )


class SqliteSmartListTagRepository(
    SqliteLeafEntityRepository[SmartListTag], SmartListTagRepository
):
    """Sqlite based smart list tags repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "smart_list_tag",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "smart_list_ref_id",
                    Integer,
                    ForeignKey("smart_list.ref_id"),
                    nullable=False,
                ),
                Column("tag_name", String(100), nullable=False),
                keep_existing=True,
            ),
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_tag_names: Optional[Iterable[SmartListTagName]] = None,
    ) -> List[SmartListTag]:
        """Find all smart list tags."""
        query_stmt = select(self._table).where(
            self._table.c.smart_list_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._table.c.archived.is_(False),
            )
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_tag_names is not None:
            query_stmt = query_stmt.where(
                self._table.c.tag_name.in_(str(fi) for fi in filter_tag_names),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def _entity_to_row(self, entity: SmartListTag) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "smart_list_ref_id": entity.smart_list.as_int(),
            "tag_name": str(entity.tag_name),
        }

    def _row_to_entity(self, row: RowType) -> SmartListTag:
        return SmartListTag(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=EntityName.from_raw(row["tag_name"]),
            smart_list=ParentLink(EntityId.from_raw(str(row["smart_list_ref_id"]))),
            tag_name=SmartListTagName.from_raw(row["tag_name"]),
        )


class SqliteSmartListItemRepository(
    SqliteLeafEntityRepository[SmartListItem], SmartListItemRepository
):
    """A repository for smart list items."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "smart_list_item",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "smart_list_ref_id",
                    Integer,
                    ForeignKey("smart_list.ref_id"),
                    nullable=False,
                ),
                Column("name", String(100), nullable=False),
                Column("is_done", Boolean, nullable=False),
                Column("tags_ref_id", JSON, nullable=False),
                Column("url", String, nullable=False),
                keep_existing=True,
            ),
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_is_done: Optional[bool] = None,
        filter_tag_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[SmartListItem]:
        """Find all smart list items."""
        query_stmt = select(self._table).where(
            self._table.c.smart_list_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._table.c.archived.is_(False),
            )
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_is_done is not None:
            query_stmt = query_stmt.where(
                self._table.c.is_done.is_(filter_is_done),
            )
        results = await self._connection.execute(query_stmt)
        all_entities = [self._row_to_entity(row) for row in results]
        if filter_tag_ref_ids is not None:
            # Can't do this in SQL that simply
            tag_set = frozenset(filter_tag_ref_ids)
            all_entities = [
                ent
                for ent in all_entities
                if len(tag_set.intersection(ent.tags_ref_id)) > 0
            ]
        return all_entities

    def _entity_to_row(self, entity: SmartListItem) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "smart_list_ref_id": entity.smart_list.as_int(),
            "name": str(entity.name),
            "is_done": entity.is_done,
            "tags_ref_id": [ti.as_int() for ti in entity.tags_ref_id],
            "url": str(entity.url) if entity.url else None,
        }

    def _row_to_entity(self, row: RowType) -> SmartListItem:
        return SmartListItem(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            smart_list=ParentLink(EntityId.from_raw(str(row["smart_list_ref_id"]))),
            name=SmartListItemName.from_raw(row["name"]),
            is_done=row["is_done"],
            tags_ref_id=[EntityId.from_raw(str(ti)) for ti in row["tags_ref_id"]],
            url=URL.from_raw(row["url"]) if row["url"] else None,
        )
