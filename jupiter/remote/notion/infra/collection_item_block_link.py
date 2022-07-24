"""A descriptor for a Notion block inside a collection item."""
from dataclasses import dataclass

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey


@dataclass(frozen=True)
class NotionCollectionItemBlockLink:
    """A descriptor for a Notion block inside a collection item."""

    position: int
    item_key: NotionLockKey
    collection_key: NotionLockKey
    the_type: str
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp

    @staticmethod
    def new(
        the_type: str,
        position: int,
        item_key: NotionLockKey,
        collection_key: NotionLockKey,
        notion_id: NotionId,
        creation_time: Timestamp,
    ) -> "NotionCollectionItemBlockLink":
        """Create a new Notion block descriptor."""
        return NotionCollectionItemBlockLink(
            position=position,
            item_key=item_key,
            collection_key=collection_key,
            the_type=the_type,
            notion_id=notion_id,
            created_time=creation_time,
            last_modified_time=creation_time,
        )

    def with_new_item(
        self, notion_id: NotionId, the_type: str, modification_time: Timestamp
    ) -> "NotionCollectionItemBlockLink":
        """Build a changed Notion link with a new Notion id."""
        return NotionCollectionItemBlockLink(
            position=self.position,
            item_key=self.item_key,
            collection_key=self.collection_key,
            the_type=the_type,
            notion_id=notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time,
        )
