"""A smart list item."""
from dataclasses import dataclass, field
from typing import Iterable, Optional, List

from domain.entity_name import EntityName
from domain.url import URL
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId, BAD_REF_ID
from framework.base.timestamp import Timestamp
from framework.event import Event
from framework.update_action import UpdateAction


@dataclass()
class SmartListItem(AggregateRoot):
    """A smart list item."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        smart_list_ref_id: EntityId
        name: EntityName
        is_done: bool
        tags_ref_id: List[EntityId]
        url: Optional[URL]
        archived: bool

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)
        is_done: UpdateAction[bool] = field(default_factory=UpdateAction.do_nothing)
        tags_ref_id: UpdateAction[List[EntityId]] = field(default_factory=UpdateAction.do_nothing)
        url: UpdateAction[Optional[URL]] = field(default_factory=UpdateAction.do_nothing)

    _smart_list_ref_id: EntityId
    _name: EntityName
    _is_done: bool
    _tags_ref_id: List[EntityId]
    _url: Optional[URL]

    @staticmethod
    def new_smart_list_item(
            archived: bool, smart_list_ref_id: EntityId, name: EntityName, is_done: bool,
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
        smart_list_item.record_event(SmartListItem.Created(
            smart_list_ref_id=smart_list_ref_id, name=name, is_done=is_done, tags_ref_id=tags_ref_id, url=url,
            archived=archived, timestamp=created_time))
        return smart_list_item

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'SmartListItem':
        """Change the name of the smart list item."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(SmartListItem.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    def change_is_done(self, is_done: bool, modification_time: Timestamp) -> 'SmartListItem':
        """Change the is done status of the smart list item."""
        if self._is_done == is_done:
            return self
        self._is_done = is_done
        self.record_event(SmartListItem.Updated(is_done=UpdateAction.change_to(is_done), timestamp=modification_time))
        return self

    def change_tags(self, tags_ref_id: List[EntityId], modification_time: Timestamp) -> 'SmartListItem':
        """Change the tags set of the smart list item."""
        if set(self._tags_ref_id) == set(tags_ref_id):
            return self
        self._tags_ref_id = tags_ref_id
        self.record_event(SmartListItem.Updated(
            tags_ref_id=UpdateAction.change_to(tags_ref_id), timestamp=modification_time))
        return self

    def change_url(self, url: Optional[URL], modification_time: Timestamp) -> 'SmartListItem':
        """Change the url of the smart list item."""
        if self._url == url:
            return self
        self._url = url
        self.record_event(SmartListItem.Updated(url=UpdateAction.change_to(url), timestamp=modification_time))
        return self

    @property
    def smart_list_ref_id(self) -> EntityId:
        """The id of the parent smart list."""
        return self._smart_list_ref_id

    @property
    def name(self) -> EntityName:
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
