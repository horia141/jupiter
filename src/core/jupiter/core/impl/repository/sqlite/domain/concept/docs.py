"""The SQLite repository for docs."""

from jupiter.core.domain.concept.docs.doc import Doc, DocRepository
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import select


class SqliteDocRepository(SqliteLeafEntityRepository[Doc], DocRepository):
    """The SQLite repository for docs."""

    async def create_if_not_exists(self, doc: Doc) -> tuple[Doc, bool]:
        """Create a doc if it doesn't exist."""
        query_stmt = select(self._table).where(
            self._table.c.idempotency_key == str(doc.idempotency_key)
        )
        result = await self._connection.execute(query_stmt)
        existing_doc = result.fetchone()
        if existing_doc:
            return self._row_to_entity(existing_doc), False
        return await super().create(doc), True
