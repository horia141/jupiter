"""Sqlite implementation of the notes repository."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.notes.infra.note_collection_repository import (
    NoteCollectionNotFoundError,
    NoteCollectionRepository,
)
from jupiter.core.domain.notes.infra.note_repository import (
    NoteNotFoundError,
    NoteRepository,
)
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.notes.note_collection import NoteCollection
from jupiter.core.domain.notes.note_content_block import NoteContentBlock
from jupiter.core.domain.notes.note_name import NoteName
from jupiter.core.domain.notes.note_source import NoteSource
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.repository import EntityAlreadyExistsError
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
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
    Unicode,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteNoteCollectionRepository(NoteCollectionRepository):
    """The note collection repository."""

    _connection: Final[AsyncConnection]
    _note_collection_table: Final[Table]
    _note_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._note_collection_table = Table(
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
        )
        self._note_collection_event_table = build_event_table(
            self._note_collection_table,
            metadata,
        )

    async def create(self, entity: NoteCollection) -> NoteCollection:
        """Create a note collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._note_collection_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._note_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: NoteCollection) -> NoteCollection:
        """Save a note collection."""
        result = await self._connection.execute(
            update(self._note_collection_table)
            .where(self._note_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise NoteCollectionNotFoundError("The note collection does not exist")
        await upsert_events(
            self._connection,
            self._note_collection_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> NoteCollection:
        """Retrieve a note collection."""
        query_stmt = select(self._note_collection_table).where(
            self._note_collection_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._note_collection_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise NoteCollectionNotFoundError(
                f"Note collection with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> NoteCollection:
        """Retrieve a note collection for a project."""
        query_stmt = select(self._note_collection_table).where(
            self._note_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise NoteCollectionNotFoundError(
                f"Note collection for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

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


class SqliteNoteRepository(NoteRepository):
    """A repository of notes."""

    _connection: Final[AsyncConnection]
    _note_table: Final[Table]
    _note_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._note_table = Table(
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
            Column(
                "parent_note_ref_id",
                Integer(),
                ForeignKey("note.ref_id"),
                nullable=True,
            ),
            Column("source", String(), nullable=False),
            Column("source_entity_ref_id", Integer(), nullable=True),
            Column("name", Unicode(), nullable=False),
            Column("content", JSON(), nullable=False),
            keep_existing=True,
        )
        self._note_event_table = build_event_table(self._note_table, metadata)

    async def create(self, entity: Note) -> Note:
        """Create a note."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._note_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    note_collection_ref_id=entity.note_collection_ref_id.as_int(),
                    parent_note_ref_id=entity.parent_note_ref_id.as_int()
                    if entity.parent_note_ref_id
                    else None,
                    source=entity.source.value,
                    source_entity_ref_id=entity.source_entity_ref_id.as_int()
                    if entity.source_entity_ref_id
                    else None,
                    name=str(entity.name),
                    content=[cb.to_json() for cb in entity.content],
                ),
            )
        except IntegrityError as err:
            raise EntityAlreadyExistsError(
                f"Note with name {entity.name} already exists",
            ) from err
        entity = entity.assign_ref_id(
            EntityId.from_raw(str(result.inserted_primary_key[0])),
        )
        await upsert_events(self._connection, self._note_event_table, entity)
        return entity

    async def save(self, entity: Note) -> Note:
        """Save a note - it should already exist."""
        result = await self._connection.execute(
            update(self._note_table)
            .where(self._note_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                note_collection_ref_id=entity.note_collection_ref_id.as_int(),
                parent_note_ref_id=entity.parent_note_ref_id.as_int()
                if entity.parent_note_ref_id
                else None,
                source=entity.source.value,
                source_entity_ref_id=entity.source_entity_ref_id.as_int()
                if entity.source_entity_ref_id
                else None,
                name=str(entity.name),
                content=[cb.to_json() for cb in entity.content],
            ),
        )
        if result.rowcount == 0:
            raise NoteNotFoundError(
                f"A note with id {entity.ref_id} does not exist",
            )
        await upsert_events(self._connection, self._note_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note:
        """Find a note by id."""
        query_stmt = select(self._note_table).where(
            self._note_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._note_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise NoteNotFoundError(f"Note identified by {ref_id} does not exist")
        return self._row_to_entity(result)

    async def load_optional_for_source(
        self,
        note_source: NoteSource,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note | None:
        """Retrieve a note via its source entity."""
        query_stmt = (
            select(self._note_table)
            .where(self._note_table.c.source == note_source.value)
            .where(
                self._note_table.c.source_entity_ref_id == source_entity_ref_id.as_int()
            )
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._note_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Note]:
        """Find all notes matching some criteria."""
        return await self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            source=NoteSource.USER,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids,
            filter_parent_note_ref_ids=None,
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        source: NoteSource,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_parent_note_ref_ids: Iterable[EntityId | None] | None = None,
        filter_source_entity_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[Note]:
        """Find all notes matching some criteria."""
        query_stmt = (
            select(self._note_table)
            .where(self._note_table.c.note_collection_ref_id == parent_ref_id.as_int())
            .where(self._note_table.c.source == source.value)
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._note_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._note_table.c.ref_id.in_([fi.as_int() for fi in filter_ref_ids])
            )
        if filter_parent_note_ref_ids is not None:
            filter_parent_note_ref_ids = list(filter_parent_note_ref_ids)  # ick
            if (
                len(filter_parent_note_ref_ids) == 1
                and filter_parent_note_ref_ids[0] is None
            ):
                query_stmt = query_stmt.where(
                    self._note_table.c.parent_note_ref_id.is_(None)
                )
            else:
                query_stmt = query_stmt.where(
                    self._note_table.c.parent_note_ref_id.in_(
                        [
                            fi.as_int() if fi else None
                            for fi in filter_parent_note_ref_ids
                        ]
                    )
                )
        if filter_source_entity_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._note_table.c.source_entity_ref_id.in_(
                    [fi.as_int() for fi in filter_source_entity_ref_ids]
                )
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Note:
        """Hard remove a note - an irreversible operation."""
        query_stmt = select(self._note_table).where(
            self._note_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise NoteNotFoundError(f"Note identified by {ref_id} does not exist")
        await self._connection.execute(
            delete(self._note_table).where(
                self._note_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._note_event_table, ref_id)
        return self._row_to_entity(result)

    async def remove_optional_for_source(
        self, note_source: NoteSource, source_entity_ref_id: EntityId
    ) -> Note | None:
        """Hard remove a note via its source."""
        query_stmt = (
            select(self._note_table)
            .where(self._note_table.c.source == note_source.value)
            .where(
                self._note_table.c.source_entity_ref_id == source_entity_ref_id.as_int()
            )
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        note = self._row_to_entity(result)
        await self._connection.execute(
            delete(self._note_table).where(
                self._note_table.c.ref_id == note.ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._note_event_table, note.ref_id)
        return note

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
            note_collection_ref_id=EntityId.from_raw(
                str(row["note_collection_ref_id"]),
            ),
            parent_note_ref_id=EntityId.from_raw(str(row["parent_note_ref_id"]))
            if row["parent_note_ref_id"]
            else None,
            source=NoteSource(row["source"]),
            source_entity_ref_id=EntityId.from_raw(str(row["source_entity_ref_id"]))
            if row["source_entity_ref_id"]
            else None,
            name=NoteName.from_raw(row["name"]),
            content=[NoteContentBlock.from_json(cb) for cb in row["content"]],
        )
