"""A Notion collection link."""
from dataclasses import dataclass
from typing import Dict

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey


@dataclass(frozen=True)
class NotionCollectionLink:
    """A descriptor for a Notion collection."""
    key: NotionLockKey
    page_notion_id: NotionId
    collection_notion_id: NotionId
    view_notion_ids: Dict[str, NotionId]
    created_time: Timestamp
    last_modified_time: Timestamp

    @staticmethod
    def new_notion_collection_link(
            key: NotionLockKey, page_notion_id: NotionId, collection_notion_id: NotionId,
            view_notion_ids: Dict[str, NotionId], modification_time: Timestamp) -> 'NotionCollectionLink':
        """Construct a Notion collection link."""
        return NotionCollectionLink(
            key=key,
            page_notion_id=page_notion_id,
            collection_notion_id=collection_notion_id,
            view_notion_ids=view_notion_ids,
            created_time=modification_time,
            last_modified_time=modification_time)

    def mark_update(self, modification_time: Timestamp) -> 'NotionCollectionLink':
        """Update the collection link to mark that an update has occurred."""
        return NotionCollectionLink(
            key=self.key,
            page_notion_id=self.page_notion_id,
            collection_notion_id=self.collection_notion_id,
            view_notion_ids=self.view_notion_ids,
            created_time=self.created_time,
            last_modified_time=modification_time)

    def with_new_collection(
            self, page_notion_id: NotionId, collection_notion_id: NotionId, view_notion_ids: Dict[str, NotionId],
            modification_time: Timestamp) -> 'NotionCollectionLink':
        """Modify this Notion collection link with a new Notion-side collection."""
        return NotionCollectionLink(
            key=self.key,
            page_notion_id=page_notion_id,
            collection_notion_id=collection_notion_id,
            view_notion_ids=view_notion_ids,
            created_time=self.created_time,
            last_modified_time=modification_time)

    def with_extra(self, name: str) -> 'NotionCollectionLinkExtra':
        """Return the Notion page info with some little extra."""
        return NotionCollectionLinkExtra(
            key=self.key,
            page_notion_id=self.page_notion_id,
            collection_notion_id=self.collection_notion_id,
            view_notion_ids=self.view_notion_ids,
            created_time=self.created_time,
            last_modified_time=self.last_modified_time,
            name=name)


@dataclass()
class NotionCollectionLinkExtra:
    """Glad we're going down the route of Windows."""
    key: NotionLockKey
    page_notion_id: NotionId
    collection_notion_id: NotionId
    view_notion_ids: Dict[str, NotionId]
    created_time: Timestamp
    last_modified_time: Timestamp
    name: str
