"""A smart list item."""
from dataclasses import dataclass
from typing import Optional, List

from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.url import URL
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.update_action import UpdateAction


@dataclass()
class SmartListItem(AggregateRoot):
    """A smart list item."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    smart_list_ref_id: EntityId
    name: SmartListItemName
    is_done: bool
    tags_ref_id: List[EntityId]
    url: Optional[URL]

    @staticmethod
    def new_smart_list_item(
            archived: bool, smart_list_ref_id: EntityId, name: SmartListItemName, is_done: bool,
            tags_ref_id: List[EntityId], url: Optional[URL], created_time: Timestamp) -> 'SmartListItem':
        """Create a smart list item."""
        smart_list_item = SmartListItem(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[],
            smart_list_ref_id=smart_list_ref_id,
            name=name,
            is_done=is_done,
            tags_ref_id=tags_ref_id,
            url=url)
        smart_list_item.record_event(SmartListItem.Created.make_event_from_frame_args(created_time))
        return smart_list_item

    def update(
            self, name: UpdateAction[SmartListItemName], is_done: UpdateAction[bool],
            tags_ref_id: UpdateAction[List[EntityId]], url: UpdateAction[Optional[URL]],
            modification_time: Timestamp) -> 'SmartListItem':
        """Update the smart list item."""
        self.name = name.or_else(self.name)
        self.is_done = is_done.or_else(self.is_done)
        self.tags_ref_id = tags_ref_id.or_else(self.tags_ref_id)
        self.url = url.or_else(self.url)
        self.record_event(SmartListItem.Updated.make_event_from_frame_args(modification_time))
        return self
