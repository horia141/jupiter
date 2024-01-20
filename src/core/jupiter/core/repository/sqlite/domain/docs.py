"""Sqlite implementation of the docs repository."""
from typing import Iterable

from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.infra.doc_collection_repository import (
    DocCollectionRepository,
)
from jupiter.core.domain.docs.infra.doc_repository import (
    DocRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteDocCollectionRepository(
    SqliteTrunkEntityRepository[DocCollection], DocCollectionRepository
):
    """The doc collection repository."""


class SqliteDocRepository(SqliteLeafEntityRepository[Doc], DocRepository):
    """A repository of docs."""

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_parent_doc_ref_ids: Iterable[EntityId | None] | None = None,
    ) -> list[Doc]:
        """Find all docs matching some criteria."""
        query_stmt = select(self._table).where(
            self._table.c.doc_collection_ref_id == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_([fi.as_int() for fi in filter_ref_ids])
            )
        if filter_parent_doc_ref_ids is not None:
            filter_parent_doc_ref_ids = list(filter_parent_doc_ref_ids)  # ick
            if (
                len(filter_parent_doc_ref_ids) == 1
                and filter_parent_doc_ref_ids[0] is None
            ):
                query_stmt = query_stmt.where(self._table.c.parent_doc_ref_id.is_(None))
            else:
                query_stmt = query_stmt.where(
                    self._table.c.parent_doc_ref_id.in_(
                        [
                            fi.as_int() if fi else None
                            for fi in filter_parent_doc_ref_ids
                        ]
                    )
                )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]
