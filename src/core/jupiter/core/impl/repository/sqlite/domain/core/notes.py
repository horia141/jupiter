"""Sqlite implementation of the notes repository."""

from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.notes.note import (
    Note,
    NoteRepository,
)
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteNoteRepository(SqliteLeafEntityRepository[Note], NoteRepository):
    """A repository of notes."""

    async def load_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason] = False,
    ) -> Note:
        """Retrieve a note via its source entity."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.domain == domain.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Note in domain {domain} with source {source_entity_ref_id!s} does not exist"
            )
        return self._row_to_entity(result)

    async def load_optional_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason] = False,
    ) -> Note | None:
        """Retrieve a note via its source entity."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.domain == domain.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)
