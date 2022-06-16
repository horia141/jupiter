"""The SQLite storage engine for Notion."""
import typing
from contextlib import contextmanager
from types import TracebackType
from typing import Final, Optional

from sqlalchemy import MetaData
from sqlalchemy.future import Engine

from jupiter.remote.notion.infra.collection_field_tag_link_repository import (
    NotionCollectionFieldTagLinkRepository,
)
from jupiter.remote.notion.infra.collection_item_link_repository import (
    NotionCollectionItemLinkRepository,
)
from jupiter.remote.notion.infra.collection_link_repository import (
    NotionCollectionLinkRepository,
)
from jupiter.remote.notion.infra.page_link_repository import NotionPageLinkRepository
from jupiter.remote.notion.infra.storage_engine import (
    NotionUnitOfWork,
    NotionStorageEngine,
)
from jupiter.repository.sqlite.connection import SqliteConnection
from jupiter.repository.sqlite.remote.notion.collection_field_tag_links import (
    SqliteNotionCollectionFieldTagLinkRepository,
)
from jupiter.repository.sqlite.remote.notion.collection_item_links import (
    SqliteNotionCollectionItemLinkRepository,
)
from jupiter.repository.sqlite.remote.notion.collection_links import (
    SqliteNotionCollectionLinkRepository,
)
from jupiter.repository.sqlite.remote.notion.page_links import (
    SqliteNotionPageLinkRepository,
)


class SqliteNotionUnitOfWork(NotionUnitOfWork):
    """The SQLite storage unit of work."""

    _notion_page_link_repository: Final[SqliteNotionPageLinkRepository]
    _notion_collection_link_repository: Final[SqliteNotionCollectionLinkRepository]
    _notion_collection_field_tag_link_repository: Final[
        SqliteNotionCollectionFieldTagLinkRepository
    ]
    _notion_collection_item_link_repository: Final[
        SqliteNotionCollectionItemLinkRepository
    ]

    def __init__(
        self,
        notion_page_link_repository: SqliteNotionPageLinkRepository,
        notion_collection_link_repository: SqliteNotionCollectionLinkRepository,
        notion_collection_field_tag_link_repository: SqliteNotionCollectionFieldTagLinkRepository,
        notion_collection_item_link_repository: SqliteNotionCollectionItemLinkRepository,
    ) -> None:
        """Constructor."""
        self._notion_page_link_repository = notion_page_link_repository
        self._notion_collection_link_repository = notion_collection_link_repository
        self._notion_collection_field_tag_link_repository = (
            notion_collection_field_tag_link_repository
        )
        self._notion_collection_item_link_repository = (
            notion_collection_item_link_repository
        )

    def __enter__(self) -> "SqliteNotionUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[typing.Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context."""

    @property
    def notion_page_link_repository(self) -> NotionPageLinkRepository:
        """The Notion page link repository."""
        return self._notion_page_link_repository

    @property
    def notion_collection_link_repository(self) -> NotionCollectionLinkRepository:
        """The Notion collection link repository."""
        return self._notion_collection_link_repository

    @property
    def notion_collection_field_tag_link_repository(
        self,
    ) -> NotionCollectionFieldTagLinkRepository:
        """The Notion collection field tag link repository."""
        return self._notion_collection_field_tag_link_repository

    @property
    def notion_collection_item_link_repository(
        self,
    ) -> NotionCollectionItemLinkRepository:
        """The Notion collection field tag link repository."""
        return self._notion_collection_item_link_repository


class SqliteNotionStorageEngine(NotionStorageEngine):
    """Sqlite based Notion storage engine."""

    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, connection: SqliteConnection) -> None:
        """Constructor."""
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[NotionUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            notion_page_link_repository = SqliteNotionPageLinkRepository(
                connection, self._metadata
            )
            notion_collection_link_repository = SqliteNotionCollectionLinkRepository(
                connection, self._metadata
            )
            notion_collection_field_tag_link_repository = (
                SqliteNotionCollectionFieldTagLinkRepository(connection, self._metadata)
            )
            notion_collection_item_link_repository = (
                SqliteNotionCollectionItemLinkRepository(connection, self._metadata)
            )
            yield SqliteNotionUnitOfWork(
                notion_page_link_repository=notion_page_link_repository,
                notion_collection_link_repository=notion_collection_link_repository,
                notion_collection_field_tag_link_repository=notion_collection_field_tag_link_repository,
                notion_collection_item_link_repository=notion_collection_item_link_repository,
            )
