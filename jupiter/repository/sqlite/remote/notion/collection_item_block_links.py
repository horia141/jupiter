"""SQLite implementation of the Notion collection item block link repository."""
from typing import Final, List

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
    Integer,
)
from sqlalchemy.engine import Connection, Result

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_item_block_link import (
    NotionCollectionItemBlockLink,
)
from jupiter.remote.notion.infra.collection_item_block_link_repository import (
    NotionCollectionItemBlockLinkRepository,
    NotionCollectionItemBlockLinkNotFoundError,
)


class SqliteNotionCollectionItemBlockLinkRepository(
    NotionCollectionItemBlockLinkRepository
):
    """SQLite implementation of the Notion collection item block Link repository."""

    _connection: Final[Connection]
    _notion_collection_item_block_link_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_collection_item_block_link_table = Table(
            "notion_collection_item_block_link",
            metadata,
            Column(
                "item_key",
                String,
                ForeignKey("notion_collection_item_link.the_key"),
                primary_key=True,
            ),
            Column("position", Integer, primary_key=True),
            Column(
                "collection_key",
                String,
                ForeignKey("notion_collection_link.the_key"),
                index=True,
            ),
            Column("the_type", String, nullable=False),
            Column("notion_id", String, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    def create(
        self, notion_collection_item_block_link: NotionCollectionItemBlockLink
    ) -> NotionCollectionItemBlockLink:
        """Create a Notion collection item block."""
        self._connection.execute(
            insert(self._notion_collection_item_block_link_table).values(
                item_key=notion_collection_item_block_link.item_key,
                position=notion_collection_item_block_link.position,
                collection_key=notion_collection_item_block_link.collection_key,
                the_type=notion_collection_item_block_link.the_type,
                notion_id=str(notion_collection_item_block_link.notion_id),
                created_time=notion_collection_item_block_link.created_time.to_db(),
                last_modified_time=notion_collection_item_block_link.last_modified_time.to_db(),
            )
        )
        return notion_collection_item_block_link

    def save(
        self, notion_collection_item_block_link: NotionCollectionItemBlockLink
    ) -> NotionCollectionItemBlockLink:
        """Save a Notion collection item block."""
        result = self._connection.execute(
            update(self._notion_collection_item_block_link_table)
            .where(
                self._notion_collection_item_block_link_table.c.item_key
                == notion_collection_item_block_link.item_key
            )
            .where(
                self._notion_collection_item_block_link_table.c.position
                == notion_collection_item_block_link.position
            )
            .values(
                the_type=notion_collection_item_block_link.the_type,
                last_modified_time=notion_collection_item_block_link.last_modified_time.to_db(),
            )
        )
        if result.rowcount == 0:
            raise NotionCollectionItemBlockLinkNotFoundError(
                "The Notion collection item block link with item key "
                + f"{notion_collection_item_block_link.item_key}:"
                + f"{notion_collection_item_block_link.position} does not exist"
            )
        return notion_collection_item_block_link

    def find_all_for_item(
        self, item_key: NotionLockKey
    ) -> List[NotionCollectionItemBlockLink]:
        """Find all Notion collection item blocks for a collection."""
        query_stmt = select(self._notion_collection_item_block_link_table).where(
            self._notion_collection_item_block_link_table.c.item_key == item_key
        )
        result = self._connection.execute(query_stmt)
        return [self._row_to_entity(r) for r in result]

    def remove(self, item_key: NotionLockKey, position: int) -> None:
        """Remove a Notion collection block item."""
        self._connection.execute(
            delete(self._notion_collection_item_block_link_table)
            .where(self._notion_collection_item_block_link_table.c.item_key == item_key)
            .where(self._notion_collection_item_block_link_table.c.position == position)
        )

    def remove_all_for_item(self, item_key: NotionLockKey) -> None:
        """Remove all Notion collection blocks for a particular item."""
        self._connection.execute(
            delete(self._notion_collection_item_block_link_table).where(
                self._notion_collection_item_block_link_table.c.item_key == item_key
            )
        )

    @staticmethod
    def _row_to_entity(row: Result) -> NotionCollectionItemBlockLink:
        return NotionCollectionItemBlockLink(
            item_key=row["item_key"],
            position=row["position"],
            collection_key=row["collection_key"],
            the_type=row["the_type"],
            notion_id=NotionId.from_raw(row["notion_id"]),
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
        )
