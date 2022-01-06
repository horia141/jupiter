"""A smart list."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.update_action import UpdateAction


@dataclass()
class SmartList(AggregateRoot):
    """A smart list."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    key: SmartListKey
    name: SmartListName

    @staticmethod
    def new_smart_list(key: SmartListKey, name: SmartListName, created_time: Timestamp) -> 'SmartList':
        """Create a smart list."""
        smart_list = SmartList(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            key=key,
            name=name)
        smart_list.record_event(SmartList.Created.make_event_from_frame_args(created_time))

        return smart_list

    def update(self, name: UpdateAction[SmartListName], modification_time: Timestamp) -> 'SmartList':
        """Change the name of the smart list."""
        self.name = name.or_else(self.name)
        self.record_event(SmartList.Updated.make_event_from_frame_args(timestamp=modification_time))
        return self
