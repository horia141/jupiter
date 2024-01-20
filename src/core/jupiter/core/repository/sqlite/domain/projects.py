"""The SQLite based projects repository."""
from typing import Iterable, List, Optional

from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import (
    ProjectRepository,
)
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteProjectCollectionRepository(
    SqliteTrunkEntityRepository[ProjectCollection], ProjectCollectionRepository
):
    """The project collection repository."""


class SqliteProjectRepository(SqliteLeafEntityRepository[Project], ProjectRepository):
    """A repository for projects."""

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Project]:
        """Find all projects."""
        query_stmt = select(self._table).where(
            self._table.c.project_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]
