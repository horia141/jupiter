"""Respository implementation for working mems."""

from jupiter.core.domain.concept.working_mem.working_mem import (
    WorkingMem,
    WorkingMemRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)


class SqliteWorkingMemRepository(
    SqliteLeafEntityRepository[WorkingMem], WorkingMemRepository
):
    """Sqlite implementation of the working mem repository."""

    async def load_latest_working_mem(
        self, working_mem_collection_ref_id: EntityId
    ) -> WorkingMem:
        """Retrieve the working mem by the latest date."""
        query_stmt = (
            self._table.select()
            .where(
                self._table.c.working_mem_collection_ref_id
                == str(working_mem_collection_ref_id)
            )
            .where(self._table.c.archived.is_(False))
            .order_by(self._table.c.created_time.desc())
            .limit(1)
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Working mem for collection {working_mem_collection_ref_id} does not exist"
            )
        return self._row_to_entity(result)
