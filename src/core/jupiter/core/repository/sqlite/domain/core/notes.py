"""Sqlite implementation of the notes repository."""
from typing import Iterable, Optional

from jupiter.core.domain.core.entity_name import NOT_USED_NAME
from jupiter.core.domain.core.notes.infra.note_collection_repository import (
    NoteCollectionRepository,
)
from jupiter.core.domain.core.notes.infra.note_repository import (
    NoteRepository,
)
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_content_block import NoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.repository import (
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


class SqliteNoteCollectionRepository(
    SqliteTrunkEntityRepository[NoteCollection], NoteCollectionRepository
):
    """The note collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "note_collection",
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

    @staticmethod
    def _entity_to_row(entity: NoteCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace_ref_id.as_int(),
        }

    @staticmethod
    def _row_to_entity(row: RowType) -> NoteCollection:
        return NoteCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])),
        )

    @staticmethod
    def _get_parent_field_name() -> str:
        return "workspace_ref_id"


class SqliteNoteRepository(SqliteLeafEntityRepository[Note], NoteRepository):
    """A repository of notes."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
                "note",
                metadata,
                Column("ref_id", Integer, primary_key=True, autoincrement=True),
                Column("version", Integer, nullable=False),
                Column("archived", Boolean, nullable=False),
                Column("created_time", DateTime, nullable=False),
                Column("last_modified_time", DateTime, nullable=False),
                Column("archived_time", DateTime, nullable=True),
                Column(
                    "note_collection_ref_id",
                    Integer,
                    ForeignKey("note_collection.ref_id"),
                    nullable=False,
                ),
                Column("domain", String(), nullable=False),
                Column("source_entity_ref_id", Integer(), nullable=False),
                Column("content", JSON(), nullable=False),
                keep_existing=True,
            ),
        )

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

    @staticmethod
    def _entity_to_row(entity: Note) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "note_collection_ref_id": entity.note_collection_ref_id.as_int(),
            "domain": entity.domain.value,
            "source_entity_ref_id": entity.source_entity_ref_id.as_int(),
            "content": [cb.to_json() for cb in entity.content],
        }

    @staticmethod
    def _row_to_entity(row: RowType) -> Note:
        return Note(
            ref_id=EntityId(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=NOT_USED_NAME,
            note_collection_ref_id=EntityId.from_raw(
                str(row["note_collection_ref_id"]),
            ),
            domain=NoteDomain(row["domain"]),
            source_entity_ref_id=EntityId.from_raw(str(row["source_entity_ref_id"])),
            content=[NoteContentBlock.from_json(cb) for cb in row["content"]],
        )

    @staticmethod
    def _get_parent_field_name() -> str:
        return "note_collection_ref_id"
