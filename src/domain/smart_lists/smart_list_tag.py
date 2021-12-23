"""A smart list tag."""
from dataclasses import dataclass, field

from domain.timestamp import Timestamp
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from framework.update_action import UpdateAction
from framework.aggregate_root import AggregateRoot
from framework.entity_id import EntityId, BAD_REF_ID
from framework.event import Event


@dataclass()
class SmartListTag(AggregateRoot):
    """A smart list tag."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        smart_list_ref_id: EntityId
        tag_name: SmartListTagName

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        tag_name: UpdateAction[SmartListTagName] = field(default_factory=UpdateAction.do_nothing)

    _smart_list_ref_id: EntityId
    _tag_name: SmartListTagName

    @staticmethod
    def new_smart_list_tag(
            smart_list_ref_id: EntityId, tag_name: SmartListTagName, created_time: Timestamp) -> 'SmartListTag':
        """Create a smart list tag."""
        smart_list_tag = SmartListTag(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _smart_list_ref_id=smart_list_ref_id,
            _tag_name=tag_name)
        smart_list_tag.record_event(
            SmartListTag.Created(smart_list_ref_id=smart_list_ref_id, tag_name=tag_name, timestamp=created_time))

        return smart_list_tag

    def change_tag_name(self, tag_name: SmartListTagName, modification_time: Timestamp) -> 'SmartListTag':
        """Change the name of the smart list."""
        if self._tag_name == tag_name:
            return self
        self._tag_name = tag_name
        self.record_event(SmartListTag.Updated(tag_name=UpdateAction.change_to(tag_name), timestamp=modification_time))
        return self

    @property
    def smart_list_ref_id(self) -> EntityId:
        """The id of the parent smart list."""
        return self._smart_list_ref_id

    @property
    def tag_name(self) -> SmartListTagName:
        """The name of the metric."""
        return self._tag_name
