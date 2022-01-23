"""A Notion page link."""
from dataclasses import dataclass

from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey


@dataclass(frozen=True)
class NotionPageLink:
    """A descriptor for a Notion page."""
    key: NotionLockKey
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp

    @staticmethod
    def new_notion_page_link(key: NotionLockKey, notion_id: NotionId, creation_time: Timestamp) -> 'NotionPageLink':
        """Create a Notion page link."""
        return NotionPageLink(
            key=key,
            notion_id=notion_id,
            created_time=creation_time,
            last_modified_time=creation_time)

    def mark_update(self, modification_time: Timestamp) -> 'NotionPageLink':
        """Update the page link to mark that an update has occurred."""
        return NotionPageLink(
            key=self.key,
            notion_id=self.notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time)

    def with_extra(self, name: str) -> 'NotionPageLinkExtra':
        """Return the Notion page info with some little extra."""
        return NotionPageLinkExtra(
            key=self.key,
            notion_id=self.notion_id,
            name=name,
            created_time=self.created_time,
            last_modified_time=self.last_modified_time)


@dataclass(frozen=True)
class NotionPageLinkExtra:
    """A descriptor for a Notion page like in Windows."""
    key: NotionLockKey
    notion_id: NotionId
    name: str
    created_time: Timestamp
    last_modified_time: Timestamp
