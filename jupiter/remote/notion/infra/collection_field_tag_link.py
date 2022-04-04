"""A descriptor for a Notion collection tag associated to a field."""
from dataclasses import dataclass

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.remote.notion.common import NotionLockKey


@dataclass(frozen=True)
class NotionCollectionFieldTagLink:
    """A descriptor for a Notion collection tag associated to a field."""

    key: NotionLockKey
    collection_key: NotionLockKey
    field: str
    ref_id: EntityId
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp

    @staticmethod
    def new_notion_collection_field_tag_link(
        key: NotionLockKey,
        collection_key: NotionLockKey,
        field: str,
        ref_id: EntityId,
        notion_id: NotionId,
        creation_time: Timestamp,
    ) -> "NotionCollectionFieldTagLink":
        """Build a new Notion collection field tag."""
        return NotionCollectionFieldTagLink(
            key=key,
            collection_key=collection_key,
            field=field,
            ref_id=ref_id,
            notion_id=notion_id,
            created_time=creation_time,
            last_modified_time=creation_time,
        )

    def mark_update(
        self, modification_time: Timestamp
    ) -> "NotionCollectionFieldTagLink":
        """Update the collection link to mark that an update has occurred."""
        return NotionCollectionFieldTagLink(
            key=self.key,
            collection_key=self.collection_key,
            field=self.field,
            ref_id=self.ref_id,
            notion_id=self.notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time,
        )

    def with_new_tag(
        self, notion_id: NotionId, modification_time: Timestamp
    ) -> "NotionCollectionFieldTagLink":
        """Build a new tag with a new Notion id."""
        return NotionCollectionFieldTagLink(
            key=self.key,
            collection_key=self.collection_key,
            field=self.field,
            ref_id=self.ref_id,
            notion_id=notion_id,
            created_time=self.created_time,
            last_modified_time=modification_time,
        )

    def with_extra(self, name: str) -> "NotionCollectionFieldTagLinkExtra":
        """Construct a version with extra data from Notion-side."""
        return NotionCollectionFieldTagLinkExtra(
            key=self.key,
            collection_key=self.collection_key,
            field=self.field,
            ref_id=self.ref_id,
            notion_id=self.notion_id,
            created_time=self.created_time,
            last_modified_time=self.last_modified_time,
            name=name,
        )


@dataclass(frozen=True)
class NotionCollectionFieldTagLinkExtra:
    """A descriptor for a Notion collection tag associated to a field."""

    key: NotionLockKey
    collection_key: NotionLockKey
    field: str
    ref_id: EntityId
    notion_id: NotionId
    created_time: Timestamp
    last_modified_time: Timestamp
    name: str
