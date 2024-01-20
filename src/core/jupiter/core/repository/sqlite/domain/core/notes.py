"""Sqlite implementation of the notes repository."""
from typing import Iterable, Optional

from jupiter.core.domain.core.notes.infra.note_collection_repository import (
    NoteCollectionRepository,
)
from jupiter.core.domain.core.notes.infra.note_repository import (
    NoteRepository,
)
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteNoteCollectionRepository(
    SqliteTrunkEntityRepository[NoteCollection], NoteCollectionRepository
):
    """The note collection repository."""


class SqliteNoteRepository(SqliteLeafEntityRepository[Note], NoteRepository):
    """A repository of notes."""

    async def load_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note:
        """Retrieve a note via its source entity."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.domain == domain.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Note in domain {domain} with source {str(source_entity_ref_id)} does not exist"
            )
        return self._row_to_entity(result)

    async def load_optional_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note | None:
        """Retrieve a note via its source entity."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.domain == domain.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        domain: Optional[NoteDomain] = None,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_source_entity_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[Note]:
        """Find all notes matching some criteria."""
        query_stmt = select(self._table).where(
            self._table.c.note_collection_ref_id == parent_ref_id.as_int()
        )
        if domain:
            query_stmt = query_stmt.where(self._table.c.domain.is_(domain.value))
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_([fi.as_int() for fi in filter_ref_ids])
            )
        if filter_source_entity_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.source_entity_ref_id.in_(
                    [fi.as_int() for fi in filter_source_entity_ref_ids]
                )
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]
