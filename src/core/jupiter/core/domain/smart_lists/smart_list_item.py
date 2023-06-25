"""A smart list item."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.core.domain.url import URL
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class SmartListItem(LeafEntity):
    """A smart list item."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    smart_list_ref_id: EntityId
    name: SmartListItemName
    is_done: bool
    tags_ref_id: List[EntityId]
    url: Optional[URL]

    @staticmethod
    def new_smart_list_item(
        archived: bool,
        smart_list_ref_id: EntityId,
        name: SmartListItemName,
        is_done: bool,
        tags_ref_id: List[EntityId],
        url: Optional[URL],
        source: EventSource,
        created_time: Timestamp,
    ) -> "SmartListItem":
        """Create a smart list item."""
        smart_list_item = SmartListItem(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                SmartListItem.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            smart_list_ref_id=smart_list_ref_id,
            name=name,
            is_done=is_done,
            tags_ref_id=tags_ref_id,
            url=url,
        )
        return smart_list_item

    def update(
        self,
        name: UpdateAction[SmartListItemName],
        is_done: UpdateAction[bool],
        tags_ref_id: UpdateAction[List[EntityId]],
        url: UpdateAction[Optional[URL]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "SmartListItem":
        """Update the smart list item."""
        return self._new_version(
            name=name.or_else(self.name),
            is_done=is_done.or_else(self.is_done),
            tags_ref_id=tags_ref_id.or_else(self.tags_ref_id),
            url=url.or_else(self.url),
            new_event=SmartListItem.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.smart_list_ref_id
