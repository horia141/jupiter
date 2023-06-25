"""A smart list."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, BranchEntity, Entity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class SmartList(BranchEntity):
    """A smart list."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    smart_list_collection_ref_id: EntityId
    name: SmartListName
    icon: Optional[EntityIcon]

    @staticmethod
    def new_smart_list(
        smart_list_collection_ref_id: EntityId,
        name: SmartListName,
        icon: Optional[EntityIcon],
        source: EventSource,
        created_time: Timestamp,
    ) -> "SmartList":
        """Create a smart list."""
        smart_list = SmartList(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                SmartList.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            smart_list_collection_ref_id=smart_list_collection_ref_id,
            name=name,
            icon=icon,
        )
        return smart_list

    def update(
        self,
        name: UpdateAction[SmartListName],
        icon: UpdateAction[Optional[EntityIcon]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "SmartList":
        """Change the name of the smart list."""
        return self._new_version(
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
            new_event=SmartList.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.smart_list_collection_ref_id
