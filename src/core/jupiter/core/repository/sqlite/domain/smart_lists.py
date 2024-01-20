"""The SQLite based smart lists repository."""
from typing import Iterable, List, Optional

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
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteBranchEntityRepository,
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteSmartListCollectionRepository(
    SqliteTrunkEntityRepository[SmartListCollection], SmartListCollectionRepository
):
    """The smart list collection repository."""


class SqliteSmartListRepository(
    SqliteBranchEntityRepository[SmartList], SmartListRepository
):
    """A repository for lists."""


class SqliteSmartListTagRepository(
    SqliteLeafEntityRepository[SmartListTag], SmartListTagRepository
):
    """Sqlite based smart list tags repository."""

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


class SqliteSmartListItemRepository(
    SqliteLeafEntityRepository[SmartListItem], SmartListItemRepository
):
    """A repository for smart list items."""

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
