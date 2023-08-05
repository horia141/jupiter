"""A smart list tag."""
from dataclasses import dataclass
from typing import cast

from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, BranchTagEntity, Entity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class SmartListTag(BranchTagEntity):
    """A smart list tag."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    smart_list_ref_id: EntityId

    @staticmethod
    def new_smart_list_tag(
        smart_list_ref_id: EntityId,
        tag_name: SmartListTagName,
        source: EventSource,
        created_time: Timestamp,
    ) -> "SmartListTag":
        """Create a smart list tag."""
        smart_list_tag = SmartListTag(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                SmartListTag.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=EntityName(tag_name.the_tag),
            smart_list_ref_id=smart_list_ref_id,
            tag_name=tag_name,
        )
        return smart_list_tag

    def update(
        self,
        tag_name: UpdateAction[SmartListTagName],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "SmartListTag":
        """Change the smart list tag."""
        return self._new_version(
            tag_name=tag_name.or_else(cast(SmartListTagName, self.tag_name)),
            new_event=SmartListTag.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.smart_list_ref_id
