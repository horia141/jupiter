"""A smart list."""
from dataclasses import dataclass

from jupiter.domain.entity_name import EntityName
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp


@dataclass()
class SmartList(AggregateRoot):
    """A smart list."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    _key: SmartListKey
    _name: EntityName

    @staticmethod
    def new_smart_list(key: SmartListKey, name: EntityName, created_time: Timestamp) -> 'SmartList':
        """Create a smart list."""
        smart_list = SmartList(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _key=key,
            _name=name)
        smart_list.record_event(SmartList.Created.make_event_from_frame_args(created_time))

        return smart_list

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'SmartList':
        """Change the name of the smart list."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(SmartList.Updated.make_event_from_frame_args(timestamp=modification_time))
        return self

    @property
    def key(self) -> SmartListKey:
        """The key of the metric."""
        return self._key

    @property
    def name(self) -> EntityName:
        """The name of the metric."""
        return self._name
