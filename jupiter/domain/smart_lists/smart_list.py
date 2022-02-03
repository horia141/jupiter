"""A smart list."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class SmartList(AggregateRoot):
    """A smart list."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    smart_list_collection_ref_id: EntityId
    key: SmartListKey
    name: SmartListName

    @staticmethod
    def new_smart_list(
            smart_list_collection_ref_id: EntityId, key: SmartListKey, name: SmartListName, source: EventSource,
            created_time: Timestamp) -> 'SmartList':
        """Create a smart list."""
        smart_list = SmartList(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[SmartList.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            smart_list_collection_ref_id=smart_list_collection_ref_id,
            key=key,
            name=name)
        return smart_list

    def update(
            self, name: UpdateAction[SmartListName], source: EventSource, modification_time: Timestamp) -> 'SmartList':
        """Change the name of the smart list."""
        return self._new_version(
            name=name.or_else(self.name),
            new_event=SmartList.Updated.make_event_from_frame_args(source, self.version, modification_time))
