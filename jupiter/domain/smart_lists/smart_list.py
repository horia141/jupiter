"""A smart list."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.entity_key import EntityKey
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.framework.entity import Entity, FIRST_VERSION, BranchEntity
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class SmartList(BranchEntity):
    """A smart list."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    smart_list_collection_ref_id: EntityId
    key: SmartListKey
    name: SmartListName
    icon: Optional[EntityIcon]

    @staticmethod
    def new_smart_list(
        smart_list_collection_ref_id: EntityId,
        key: SmartListKey,
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
                    source, FIRST_VERSION, created_time
                )
            ],
            smart_list_collection_ref_id=smart_list_collection_ref_id,
            key=key,
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
                source, self.version, modification_time
            ),
        )

    @property
    def branch_key(self) -> EntityKey:
        """The key."""
        return self.key

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.smart_list_collection_ref_id
