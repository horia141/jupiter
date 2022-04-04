"""SQLite implementation of the Notion collection link repository."""
from typing import Optional, Final

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
    JSON,
)
from sqlalchemy.engine import Connection, Result

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_link import NotionCollectionLink
from jupiter.remote.notion.infra.collection_link_repository import (
    NotionCollectionLinkRepository,
    NotionCollectionLinkNotFoundError,
)


class SqliteNotionCollectionLinkRepository(NotionCollectionLinkRepository):
    """SQLite implementation of the Notion collection link repository."""

    _connection: Final[Connection]
    _notion_collection_link_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_collection_link_table = Table(
            "notion_collection_link",
            metadata,
            Column("the_key", String, primary_key=True),
            Column("page_notion_id", String, nullable=False),
            Column("collection_notion_id", String, nullable=False),
            Column("view_notion_ids", JSON, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    def create(
        self, notion_collection_link: NotionCollectionLink
    ) -> NotionCollectionLink:
        """Create a Notion collection."""
        self._connection.execute(
            insert(self._notion_collection_link_table).values(
                the_key=notion_collection_link.key,
                page_notion_id=str(notion_collection_link.page_notion_id),
                collection_notion_id=str(notion_collection_link.collection_notion_id),
                view_notion_ids={
                    k: str(v) for k, v in notion_collection_link.view_notion_ids.items()
                },
                created_time=notion_collection_link.created_time.to_db(),
                last_modified_time=notion_collection_link.last_modified_time.to_db(),
            )
        )
        return notion_collection_link

    def save(
        self, notion_collection_link: NotionCollectionLink
    ) -> NotionCollectionLink:
        """Save a Notion collection."""
        result = self._connection.execute(
            update(self._notion_collection_link_table)
            .where(
                self._notion_collection_link_table.c.the_key
                == notion_collection_link.key
            )
            .values(
                page_notion_id=str(notion_collection_link.page_notion_id),
                collection_notion_id=str(notion_collection_link.collection_notion_id),
                view_notion_ids={
                    k: str(v) for k, v in notion_collection_link.view_notion_ids.items()
                },
                last_modified_time=notion_collection_link.last_modified_time.to_db(),
            )
        )
        if result.rowcount == 0:
            raise NotionCollectionLinkNotFoundError(
                f"The Notion collection link with key {notion_collection_link.key} does not exist"
            )
        return notion_collection_link

    def load(self, key: NotionLockKey) -> NotionCollectionLink:
        """Load a Notion collection."""
        query_stmt = select(self._notion_collection_link_table).where(
            self._notion_collection_link_table.c.the_key == key
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise NotionCollectionLinkNotFoundError(
                f"The Notion collection link with key {key} does not exist"
            )
        return self._row_to_entity(result)

    def load_optional(self, key: NotionLockKey) -> Optional[NotionCollectionLink]:
        """Load a Notion collection or return None if there isn't one."""
        query_stmt = select(self._notion_collection_link_table).where(
            self._notion_collection_link_table.c.the_key == key
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    def remove(self, key: NotionLockKey) -> None:
        """Remove the Notion collection."""
        self._connection.execute(
            delete(self._notion_collection_link_table).where(
                self._notion_collection_link_table.c.the_key == key
            )
        )

    @staticmethod
    def _row_to_entity(row: Result) -> NotionCollectionLink:
        return NotionCollectionLink(
            key=row["the_key"],
            page_notion_id=NotionId.from_raw(row["page_notion_id"]),
            collection_notion_id=NotionId.from_raw(row["collection_notion_id"]),
            view_notion_ids={
                k: NotionId.from_raw(v) for k, v in row["view_notion_ids"].items()
            },
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
        )
