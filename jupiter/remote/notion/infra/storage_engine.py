"""Notion specific storage interaction."""
import abc
from contextlib import contextmanager
from typing import Iterator

from jupiter.remote.notion.infra.collection_field_tag_link_repository import (
    NotionCollectionFieldTagLinkRepository,
)
from jupiter.remote.notion.infra.collection_item_block_link_repository import (
    NotionCollectionItemBlockLinkRepository,
)
from jupiter.remote.notion.infra.collection_item_link_repository import (
    NotionCollectionItemLinkRepository,
)
from jupiter.remote.notion.infra.collection_link_repository import (
    NotionCollectionLinkRepository,
)
from jupiter.remote.notion.infra.page_link_repository import NotionPageLinkRepository


class NotionUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def notion_page_link_repository(self) -> NotionPageLinkRepository:
        """The Notion page link repository."""

    @property
    @abc.abstractmethod
    def notion_collection_link_repository(self) -> NotionCollectionLinkRepository:
        """The Notion collection link repository."""

    @property
    @abc.abstractmethod
    def notion_collection_field_tag_link_repository(
        self,
    ) -> NotionCollectionFieldTagLinkRepository:
        """The Notion collection field tag link repository."""

    @property
    @abc.abstractmethod
    def notion_collection_item_link_repository(
        self,
    ) -> NotionCollectionItemLinkRepository:
        """The Notion collection item link repository."""

    @property
    @abc.abstractmethod
    def notion_collection_item_block_link_repository(
        self,
    ) -> NotionCollectionItemBlockLinkRepository:
        """The Notion collection item block link repository."""


class NotionStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[NotionUnitOfWork]:
        """Build a unit of work."""
