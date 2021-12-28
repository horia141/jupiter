"""A smart list tag."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp


@dataclass()
class SmartListTag(AggregateRoot):
    """A smart list tag."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

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
        smart_list_tag.record_event(SmartListTag.Created.make_event_from_frame_args(created_time))

        return smart_list_tag

    def change_tag_name(self, tag_name: SmartListTagName, modification_time: Timestamp) -> 'SmartListTag':
        """Change the name of the smart list."""
        if self._tag_name == tag_name:
            return self
        self._tag_name = tag_name
        self.record_event(SmartListTag.Updated.make_event_from_frame_args(modification_time))
        return self

    @property
    def smart_list_ref_id(self) -> EntityId:
        """The id of the parent smart list."""
        return self._smart_list_ref_id

    @property
    def tag_name(self) -> SmartListTagName:
        """The name of the metric."""
        return self._tag_name
