"""A smart list."""
from dataclasses import dataclass, field

from domain.timestamp import Timestamp
from domain.entity_name import EntityName
from domain.smart_lists.smart_list_key import SmartListKey
from models.framework import AggregateRoot, Event, UpdateAction, BAD_REF_ID


@dataclass()
class SmartList(AggregateRoot):
    """A smart list."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        key: SmartListKey
        name: EntityName

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)

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
        smart_list.record_event(SmartList.Created(key=key, name=name, timestamp=created_time))

        return smart_list

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'SmartList':
        """Change the name of the smart list."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(SmartList.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    @property
    def key(self) -> SmartListKey:
        """The key of the metric."""
        return self._key

    @property
    def name(self) -> EntityName:
        """The name of the metric."""
        return self._name
