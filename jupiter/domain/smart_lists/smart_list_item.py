"""A smart list item."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.url import URL
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp


@dataclass()
class SmartListItem(AggregateRoot):
    """A smart list item."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    _smart_list_ref_id: EntityId
    _name: SmartListItemName
    _is_done: bool
    _tags_ref_id: List[EntityId]
    _url: Optional[URL]

    @staticmethod
    def new_smart_list_item(
            archived: bool, smart_list_ref_id: EntityId, name: SmartListItemName, is_done: bool,
            tags_ref_id: List[EntityId], url: Optional[URL], created_time: Timestamp) -> 'SmartListItem':
        """Create a smart list item."""
        smart_list_item = SmartListItem(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _smart_list_ref_id=smart_list_ref_id,
            _name=name,
            _is_done=is_done,
            _tags_ref_id=tags_ref_id,
            _url=url)
        smart_list_item.record_event(SmartListItem.Created.make_event_from_frame_args(created_time))
        return smart_list_item

    def change_name(self, name: SmartListItemName, modification_time: Timestamp) -> 'SmartListItem':
        """Change the name of the smart list item."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(SmartListItem.Updated.make_event_from_frame_args(modification_time))
        return self

    def change_is_done(self, is_done: bool, modification_time: Timestamp) -> 'SmartListItem':
        """Change the is done status of the smart list item."""
        if self._is_done == is_done:
            return self
        self._is_done = is_done
        self.record_event(SmartListItem.Updated.make_event_from_frame_args(modification_time))
        return self

    def change_tags(self, tags_ref_id: List[EntityId], modification_time: Timestamp) -> 'SmartListItem':
        """Change the tags set of the smart list item."""
        if set(self._tags_ref_id) == set(tags_ref_id):
            return self
        self._tags_ref_id = tags_ref_id
        self.record_event(SmartListItem.Updated.make_event_from_frame_args(modification_time))
        return self

    def change_url(self, url: Optional[URL], modification_time: Timestamp) -> 'SmartListItem':
        """Change the url of the smart list item."""
        if self._url == url:
            return self
        self._url = url
        self.record_event(SmartListItem.Updated.make_event_from_frame_args(timestamp=modification_time))
        return self

    @property
    def smart_list_ref_id(self) -> EntityId:
        """The id of the parent smart list."""
        return self._smart_list_ref_id

    @property
    def name(self) -> SmartListItemName:
        """The item name."""
        return self._name

    @property
    def is_done(self) -> bool:
        """Whether this is done or not."""
        return self._is_done

    @property
    def tags(self) -> Iterable[EntityId]:
        """The tag set for the entities."""
        return self._tags_ref_id

    @property
    def url(self) -> Optional[URL]:
        """The url for the item."""
        return self._url
