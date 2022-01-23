"""SQLite implementation of the Notion collection field tag link repository."""
from typing import Optional, Final, Iterable

from sqlalchemy import insert, MetaData, Table, Column, DateTime, String, update, select, delete, ForeignKey
from sqlalchemy.engine import Connection, Result

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_field_tag_link import NotionCollectionFieldTagLink
from jupiter.remote.notion.infra.collection_field_tag_link_repository \
    import NotionCollectionFieldTagLinkRepository, NotionCollectionFieldTagLinkNotFoundError


class SqliteNotionCollectionFieldTagLinkRepository(NotionCollectionFieldTagLinkRepository):
    """SQLite implementation of the Notion collection field tag link repository."""

    _connection: Final[Connection]
    _notion_collection_field_tag_link_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_collection_field_tag_link_table = Table(
            'notion_collection_field_tag_link',
            metadata,
            Column('the_key', String, primary_key=True),
            Column('collection_key', String, ForeignKey('notion_collection_link.the_key'), index=True),
            Column('field', String, nullable=False),
            Column('ref_id', String, nullable=False),
            Column('notion_id', String, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            keep_existing=True)

    def create(self, notion_collection_field_tag_link: NotionCollectionFieldTagLink) -> NotionCollectionFieldTagLink:
        """Create a Notion collection field tag."""
        self._connection.execute(
            insert(self._notion_collection_field_tag_link_table).values(
                the_key=notion_collection_field_tag_link.key,
                collection_key=notion_collection_field_tag_link.collection_key,
                field=notion_collection_field_tag_link.field,
                ref_id=str(notion_collection_field_tag_link.ref_id),
                notion_id=str(notion_collection_field_tag_link.notion_id),
                created_time=notion_collection_field_tag_link.created_time.to_db(),
                last_modified_time=notion_collection_field_tag_link.last_modified_time.to_db()))
        return notion_collection_field_tag_link

    def save(self, notion_collection_field_tag_link: NotionCollectionFieldTagLink) -> NotionCollectionFieldTagLink:
        """Save a Notion collection field tag."""
        result = self._connection.execute(
            update(self._notion_collection_field_tag_link_table)
            .where(self._notion_collection_field_tag_link_table.c.the_key == notion_collection_field_tag_link.key)
            .values(
                notion_id=str(notion_collection_field_tag_link.notion_id),
                last_modified_time=notion_collection_field_tag_link.last_modified_time.to_db()))
        if result.rowcount == 0:
            raise NotionCollectionFieldTagLinkNotFoundError(
                f"The Notion collection field tag link with key {notion_collection_field_tag_link.key} does not exist")
        return notion_collection_field_tag_link

    def load(self, key: NotionLockKey) -> NotionCollectionFieldTagLink:
        """Load a Notion collection field tag."""
        query_stmt = \
            select(self._notion_collection_field_tag_link_table)\
            .where(self._notion_collection_field_tag_link_table.c.the_key == key)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise NotionCollectionFieldTagLinkNotFoundError(
                f"The Notion collection field tag link with key {key} does not exist")
        return self._row_to_entity(result)

    def load_optional(self, key: NotionLockKey) -> Optional[NotionCollectionFieldTagLink]:
        """Load a Notion collection field tag or return None if not found."""
        query_stmt = select(self._notion_collection_field_tag_link_table)\
            .where(self._notion_collection_field_tag_link_table.c.the_key == key)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    def find_all_for_collection(
            self, collection_key: NotionLockKey, field: str) -> Iterable[NotionCollectionFieldTagLink]:
        """Find all Notion collection field tags for a collection and field."""
        query_stmt = \
            select(self._notion_collection_field_tag_link_table)\
            .where(self._notion_collection_field_tag_link_table.c.collection_key == collection_key)\
            .where(self._notion_collection_field_tag_link_table.c.field == field)
        result = self._connection.execute(query_stmt)
        return [self._row_to_entity(r) for r in result]

    def remove(self, key: NotionLockKey) -> None:
        """Remove a Notion collection field tag."""
        self._connection.execute(
            delete(self._notion_collection_field_tag_link_table)
            .where(self._notion_collection_field_tag_link_table.c.the_key == key))

    @staticmethod
    def _row_to_entity(row: Result) -> NotionCollectionFieldTagLink:
        return NotionCollectionFieldTagLink(
            key=row["the_key"],
            collection_key=row["collection_key"],
            field=row["field"],
            ref_id=EntityId.from_raw(row["ref_id"]),
            notion_id=NotionId.from_raw(row["notion_id"]),
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]))
