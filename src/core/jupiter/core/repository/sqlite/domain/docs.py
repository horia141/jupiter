"""Sqlite implementation of the docs repository."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.docs.infra.doc_collection_repository import (
    DocCollectionNotFoundError,
    DocCollectionRepository,
)
from jupiter.core.domain.docs.infra.doc_repository import (
    DocNotFoundError,
    DocRepository,
)
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.framework.repository import EntityAlreadyExistsError
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Unicode,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteDocCollectionRepository(DocCollectionRepository):
    """The doc collection repository."""

    _connection: Final[AsyncConnection]
    _doc_collection_table: Final[Table]
    _doc_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._doc_collection_table = Table(
            "doc_collection",
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
        self._doc_collection_event_table = build_event_table(
            self._doc_collection_table,
            metadata,
        )

    async def create(self, entity: DocCollection) -> DocCollection:
        """Create a doc collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._doc_collection_table).values(
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
            self._doc_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: DocCollection) -> DocCollection:
        """Save a doc collection."""
        result = await self._connection.execute(
            update(self._doc_collection_table)
            .where(self._doc_collection_table.c.ref_id == entity.ref_id.as_int())
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
            raise DocCollectionNotFoundError("The doc collection does not exist")
        await upsert_events(
            self._connection,
            self._doc_collection_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> DocCollection:
        """Retrieve a doc collection."""
        query_stmt = select(self._doc_collection_table).where(
            self._doc_collection_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._doc_collection_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise DocCollectionNotFoundError(
                f"Doc collection with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> DocCollection:
        """Retrieve a doc collection for a project."""
        query_stmt = select(self._doc_collection_table).where(
            self._doc_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise DocCollectionNotFoundError(
                f"Doc collection for workspace {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> DocCollection:
        return DocCollection(
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


class SqliteDocRepository(DocRepository):
    """A repository of docs."""

    _connection: Final[AsyncConnection]
    _doc_table: Final[Table]
    _doc_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._doc_table = Table(
            "doc",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "doc_collection_ref_id",
                Integer,
                ForeignKey("doc_collection.ref_id"),
                nullable=False,
            ),
            Column(
                "parent_doc_ref_id",
                Integer(),
                ForeignKey("doc.ref_id"),
                nullable=True,
            ),
            Column("name", Unicode(), nullable=False),
            keep_existing=True,
        )
        self._doc_event_table = build_event_table(self._doc_table, metadata)

    async def create(self, entity: Doc) -> Doc:
        """Create a doc."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._doc_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    doc_collection_ref_id=entity.doc_collection_ref_id.as_int(),
                    parent_doc_ref_id=entity.parent_doc_ref_id.as_int()
                    if entity.parent_doc_ref_id
                    else None,
                    name=str(entity.name),
                ),
            )
        except IntegrityError as err:
            raise EntityAlreadyExistsError(
                f"Doc with name {entity.name} already exists",
            ) from err
        entity = entity.assign_ref_id(
            EntityId.from_raw(str(result.inserted_primary_key[0])),
        )
        await upsert_events(self._connection, self._doc_event_table, entity)
        return entity

    async def save(self, entity: Doc) -> Doc:
        """Save a doc - it should already exist."""
        result = await self._connection.execute(
            update(self._doc_table)
            .where(self._doc_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                doc_collection_ref_id=entity.doc_collection_ref_id.as_int(),
                parent_doc_ref_id=entity.parent_doc_ref_id.as_int()
                if entity.parent_doc_ref_id
                else None,
                name=str(entity.name),
            ),
        )
        if result.rowcount == 0:
            raise DocNotFoundError(
                f"A doc with id {entity.ref_id} does not exist",
            )
        await upsert_events(self._connection, self._doc_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Doc:
        """Find a doc by id."""
        query_stmt = select(self._doc_table).where(
            self._doc_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._doc_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise DocNotFoundError(f"Doc identified by {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Doc]:
        """Find all docs matching some criteria."""
        return await self.find_all_with_filters(
            parent_ref_id=parent_ref_id,
            allow_archived=allow_archived,
            filter_ref_ids=filter_ref_ids,
            filter_parent_doc_ref_ids=None,
        )

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_parent_doc_ref_ids: Iterable[EntityId | None] | None = None,
    ) -> list[Doc]:
        """Find all docs matching some criteria."""
        query_stmt = select(self._doc_table).where(
            self._doc_table.c.doc_collection_ref_id == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._doc_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._doc_table.c.ref_id.in_([fi.as_int() for fi in filter_ref_ids])
            )
        if filter_parent_doc_ref_ids is not None:
            filter_parent_doc_ref_ids = list(filter_parent_doc_ref_ids)  # ick
            if (
                len(filter_parent_doc_ref_ids) == 1
                and filter_parent_doc_ref_ids[0] is None
            ):
                query_stmt = query_stmt.where(
                    self._doc_table.c.parent_doc_ref_id.is_(None)
                )
            else:
                query_stmt = query_stmt.where(
                    self._doc_table.c.parent_doc_ref_id.in_(
                        [
                            fi.as_int() if fi else None
                            for fi in filter_parent_doc_ref_ids
                        ]
                    )
                )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[Doc]:
        """Find all cocs with generic filters."""
        query_stmt = select(self._doc_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._doc_table.c.archived.is_(False))

        query_stmt = compile_query_relative_to(query_stmt, self._doc_table, kwargs)

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Doc:
        """Hard remove a doc - an irreversible operation."""
        query_stmt = select(self._doc_table).where(
            self._doc_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise DocNotFoundError(f"Doc identified by {ref_id} does not exist")
        await self._connection.execute(
            delete(self._doc_table).where(
                self._doc_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._doc_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Doc:
        return Doc(
            ref_id=EntityId(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            doc_collection_ref_id=EntityId.from_raw(
                str(row["doc_collection_ref_id"]),
            ),
            parent_doc_ref_id=EntityId.from_raw(str(row["parent_doc_ref_id"]))
            if row["parent_doc_ref_id"]
            else None,
            name=DocName.from_raw(row["name"]),
        )
