"""Sqlite implementation of the docs repository."""
from typing import Iterable

from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.docs.infra.doc_collection_repository import (
    DocCollectionRepository,
)
from jupiter.core.domain.docs.infra.doc_repository import (
    DocRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
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
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteDocCollectionRepository(
    SqliteTrunkEntityRepository[DocCollection], DocCollectionRepository
):
    """The doc collection repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    @staticmethod
    def _entity_to_row(entity: DocCollection) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
        }

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
            workspace=ParentLink(EntityId.from_raw(str(row["workspace_ref_id"]))),
        )


class SqliteDocRepository(SqliteLeafEntityRepository[Doc], DocRepository):
    """A repository of docs."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

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

    @staticmethod
    def _entity_to_row(entity: Doc) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "doc_collection_ref_id": entity.doc_collection.as_int(),
            "parent_doc_ref_id": entity.parent_doc_ref_id.as_int()
            if entity.parent_doc_ref_id
            else None,
            "name": str(entity.name),
        }

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
            doc_collection=ParentLink(
                EntityId.from_raw(
                    str(row["doc_collection_ref_id"]),
                )
            ),
            parent_doc_ref_id=EntityId.from_raw(str(row["parent_doc_ref_id"]))
            if row["parent_doc_ref_id"]
            else None,
            name=DocName.from_raw(row["name"]),
        )
