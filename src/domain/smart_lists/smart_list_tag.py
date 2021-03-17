"""A smart list tag."""
from dataclasses import dataclass, field

from models.basic import Timestamp, EntityId, Tag
from models.framework import AggregateRoot, Event, BAD_REF_ID, UpdateAction


@dataclass()
class SmartListTag(AggregateRoot):
    """A smart list tag."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        smart_list_ref_id: EntityId
        name: Tag

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[Tag] = field(default_factory=UpdateAction.do_nothing)

    _smart_list_ref_id: EntityId
    _name: Tag

    @staticmethod
    def new_smart_list_tag(smart_list_ref_id: EntityId, name: Tag, created_time: Timestamp) -> 'SmartListTag':
        """Create a smart list tag."""
        smart_list_tag = SmartListTag(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _smart_list_ref_id=smart_list_ref_id,
            _name=name)
        smart_list_tag.record_event(
            SmartListTag.Created(smart_list_ref_id=smart_list_ref_id, name=name, timestamp=created_time))

        return smart_list_tag

    def change_name(self, name: Tag, modification_time: Timestamp) -> 'SmartListTag':
        """Change the name of the smart list."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(SmartListTag.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    @property
    def smart_list_ref_id(self) -> EntityId:
        """The id of the parent smart list."""
        return self._smart_list_ref_id

    @property
    def name(self) -> Tag:
        """The name of the metric."""
        return self._name
