"""A descriptor for a Notion collection item."""
from dataclasses import dataclass
from typing import Generic, TypeVar, Any

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionLeafEntity
from jupiter.remote.notion.common import NotionLockKey

ItemT = TypeVar("ItemT", bound=NotionLeafEntity[Any, Any, Any])


@dataclass(frozen=True)
class NotionCollectionItemLink:
    """A descriptor for a Notion collection item."""

    key: NotionLockKey
    collection_key: NotionLockKey
    ref_id: EntityId
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp

    @staticmethod
    def new_notion_collection_item_link(
            key: NotionLockKey, collection_key: NotionLockKey, ref_id: EntityId,
            notion_id: NotionId, creation_time: Timestamp) -> 'NotionCollectionItemLink':
        """Build a new Notion collection item link."""
        return NotionCollectionItemLink(
            key=key,
            collection_key=collection_key,
            ref_id=ref_id,
            notion_id=notion_id,
            created_time=creation_time,
            last_modified_time=creation_time)

    def mark_update(self, modification_time: Timestamp) -> 'NotionCollectionItemLink':
        """Update the collection link to mark that an update has occurred."""
        return NotionCollectionItemLink(
            key=self.key,
            collection_key=self.collection_key,
            ref_id=self.ref_id,
            notion_id=self.notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time)

    def with_new_item(self, notion_id: NotionId, modification_time: Timestamp) -> 'NotionCollectionItemLink':
        """Build a changed Notion link with a new Notion id."""
        return NotionCollectionItemLink(
            key=self.key,
            collection_key=self.collection_key,
            ref_id=self.ref_id,
            notion_id=notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time)

    def with_extra(self, item_info: ItemT) -> 'NotionCollectionItemLinkExtra[ItemT]':
        """Construct a new version of this with the extra Notion-side info."""
        return NotionCollectionItemLinkExtra(
            key=self.key,
            collection_key=self.collection_key,
            ref_id=self.ref_id,
            notion_id=self.notion_id,
            created_time=self.created_time,
            last_modified_time=self.last_modified_time,
            item_info=item_info)


@dataclass(frozen=True)
class NotionCollectionItemLinkExtra(Generic[ItemT]):
    """A descriptor for a Notion collection tag associated to a field."""
    key: NotionLockKey
    collection_key: NotionLockKey
    ref_id: EntityId
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp
    item_info: ItemT
