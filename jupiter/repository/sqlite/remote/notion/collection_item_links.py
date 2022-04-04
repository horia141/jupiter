"""SQLite implementation of the Notion collection item link repository."""
from typing import Optional, Final, Iterable

from sqlalchemy import (
    insert,
    MetaData,
    Table,
    Column,
    DateTime,
    String,
    update,
    select,
    delete,
    ForeignKey,
)
from sqlalchemy.engine import Connection, Result

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_item_link import NotionCollectionItemLink
from jupiter.remote.notion.infra.collection_item_link_repository import (
    NotionCollectionItemLinkRepository,
    NotionCollectionItemLinkNotFoundError,
)


class SqliteNotionCollectionItemLinkRepository(NotionCollectionItemLinkRepository):
    """SQLite implementation of the Notion collection item Link repository."""

    _connection: Final[Connection]
    _notion_collection_item_link_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_collection_item_link_table = Table(
            "notion_collection_item_link",
            metadata,
            Column("the_key", String, primary_key=True),
            Column(
                "collection_key",
                String,
                ForeignKey("notion_collection_link.the_key"),
                index=True,
            ),
            Column("ref_id", String, nullable=False),
            Column("notion_id", String, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    def create(
        self, notion_collection_item_link: NotionCollectionItemLink
    ) -> NotionCollectionItemLink:
        """Create a Notion collection item."""
        self._connection.execute(
            insert(self._notion_collection_item_link_table).values(
                the_key=notion_collection_item_link.key,
                collection_key=notion_collection_item_link.collection_key,
                ref_id=str(notion_collection_item_link.ref_id),
                notion_id=str(notion_collection_item_link.notion_id),
                created_time=notion_collection_item_link.created_time.to_db(),
                last_modified_time=notion_collection_item_link.last_modified_time.to_db(),
            )
        )
        return notion_collection_item_link

    def save(
        self, notion_collection_item_link: NotionCollectionItemLink
    ) -> NotionCollectionItemLink:
        """Save a Notion collection item."""
        result = self._connection.execute(
            update(self._notion_collection_item_link_table)
            .where(
                self._notion_collection_item_link_table.c.the_key
                == notion_collection_item_link.key
            )
            .values(
                notion_id=str(notion_collection_item_link.notion_id),
                last_modified_time=notion_collection_item_link.last_modified_time.to_db(),
            )
        )
        if result.rowcount == 0:
            raise NotionCollectionItemLinkNotFoundError(
                f"The Notion collection item link with key {notion_collection_item_link.key} does not exist"
            )
        return notion_collection_item_link

    def load(self, key: NotionLockKey) -> NotionCollectionItemLink:
        """Load a Notion collection item."""
        query_stmt = select(self._notion_collection_item_link_table).where(
            self._notion_collection_item_link_table.c.the_key == key
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise NotionCollectionItemLinkNotFoundError(
                f"The Notion collection item link with key {key} does not exist"
            )
        return self._row_to_entity(result)

    def load_optional(self, key: NotionLockKey) -> Optional[NotionCollectionItemLink]:
        """Load a Notion collection item or return None if absent."""
        query_stmt = select(self._notion_collection_item_link_table).where(
            self._notion_collection_item_link_table.c.the_key == key
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    def find_all_for_collection(
        self, collection_key: NotionLockKey
    ) -> Iterable[NotionCollectionItemLink]:
        """Find all Notion collection items for a collection."""
        query_stmt = select(self._notion_collection_item_link_table).where(
            self._notion_collection_item_link_table.c.collection_key == collection_key
        )
        result = self._connection.execute(query_stmt)
        return [self._row_to_entity(r) for r in result]

    def remove(self, key: NotionLockKey) -> None:
        """Remove a Notion collection item."""
        self._connection.execute(
            delete(self._notion_collection_item_link_table).where(
                self._notion_collection_item_link_table.c.the_key == key
            )
        )

    @staticmethod
    def _row_to_entity(row: Result) -> NotionCollectionItemLink:
        return NotionCollectionItemLink(
            key=row["the_key"],
            collection_key=row["collection_key"],
            ref_id=EntityId.from_raw(row["ref_id"]),
            notion_id=NotionId.from_raw(row["notion_id"]),
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
        )
