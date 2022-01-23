"""SQLite implementation of the Notion Page Link repository."""
from typing import Optional, Final

from sqlalchemy import insert, MetaData, Table, Column, DateTime, String, update, select, delete
from sqlalchemy.engine import Connection, Result

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.page_link import NotionPageLink
from jupiter.remote.notion.infra.page_link_repository import NotionPageLinkRepository, NotionPageLinkNotFoundError


class SqliteNotionPageLinkRepository(NotionPageLinkRepository):
    """SQLite implementation of the Notion Page Link repository."""

    _connection: Final[Connection]
    _notion_page_link_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._notion_page_link_table = Table(
            'notion_page_link',
            metadata,
            Column('the_key', String, primary_key=True),
            Column('notion_id', String, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            keep_existing=True)

    def create(self, notion_page_link: NotionPageLink) -> NotionPageLink:
        """Create a Notion page."""
        self._connection.execute(
            insert(self._notion_page_link_table).values(
                the_key=notion_page_link.key,
                notion_id=str(notion_page_link.notion_id),
                created_time=notion_page_link.created_time.to_db(),
                last_modified_time=notion_page_link.last_modified_time.to_db()))
        return notion_page_link

    def save(self, notion_page_link: NotionPageLink) -> NotionPageLink:
        """Save a Notion page."""
        result = self._connection.execute(
            update(self._notion_page_link_table)
            .where(self._notion_page_link_table.c.the_key == notion_page_link.key)
            .values(
                notion_id=str(notion_page_link.notion_id),
                last_modified_time=notion_page_link.last_modified_time.to_db()))
        if result.rowcount == 0:
            raise NotionPageLinkNotFoundError(f"The Notion page link with key {notion_page_link.key} does not exist")
        return notion_page_link

    def load(self, key: NotionLockKey) -> NotionPageLink:
        """Load a Notion page."""
        query_stmt = select(self._notion_page_link_table).where(self._notion_page_link_table.c.the_key == key)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise NotionPageLinkNotFoundError(f"The Notion page link with key {key} does not exist")
        return self._row_to_entity(result)

    def load_optional(self, key: NotionLockKey) -> Optional[NotionPageLink]:
        """Load a Notion page or return None if there isn't one."""
        query_stmt = select(self._notion_page_link_table).where(self._notion_page_link_table.c.the_key == key)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    def remove(self, key: NotionLockKey) -> None:
        """Remove a Notion page."""
        self._connection.execute(
            delete(self._notion_page_link_table)
            .where(self._notion_page_link_table.c.the_key == key))

    @staticmethod
    def _row_to_entity(row: Result) -> NotionPageLink:
        return NotionPageLink(
            key=row["the_key"],
            notion_id=NotionId.from_raw(row["notion_id"]),
            created_time=Timestamp.from_db(row["created_time"]),
            last_modified_time=Timestamp.from_db(row["last_modified_time"]))
