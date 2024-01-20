"""The SQLite base habits repository."""
from typing import Iterable, List, Optional

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import (
    HabitRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteHabitCollectionRepository(
    SqliteTrunkEntityRepository[HabitCollection], HabitCollectionRepository
):
    """The habit collection repository."""


class SqliteHabitRepository(SqliteLeafEntityRepository[Habit], HabitRepository):
    """Sqlite based habit repository."""

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Habit]:
        """Retrieve habit."""
        query_stmt = select(self._table).where(
            self._table.c.habit_collection_ref_id == parent_ref_id.as_int(),
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
