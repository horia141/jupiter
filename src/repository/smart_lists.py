"""Repository for smart lists."""
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Iterable, ClassVar, Final, Set, List
import typing

from models.basic import EntityId, SmartListKey, Tag, ModelValidationError
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, In, Eq, Intersect
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartListRow(BaseEntityRow):
    """A container for smart list items."""
    key: SmartListKey
    name: str


class SmartListsRepository:
    """A repository for lists."""

    _SMART_LISTS_FILE_PATH: ClassVar[Path] = Path("./smart-lists.yaml")

    _storage: Final[EntitiesStorage[SmartListRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[SmartListRow](self._SMART_LISTS_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'SmartListsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_smart_list(self, key: SmartListKey, name: str, archived: bool) -> SmartListRow:
        """Create a list."""
        new_smart_list = SmartListRow(key=key, name=name, archived=archived)
        return self._storage.create(new_smart_list)

    def archive_smart_list(self, ref_id: EntityId) -> SmartListRow:
        """Archive a list."""
        return self._storage.archive(ref_id)

    def remove_smart_list(self, ref_id: EntityId) -> SmartListRow:
        """Hard remove a smart list."""
        return self._storage.remove(ref_id=ref_id)

    def update_smart_list(
            self, new_smart_list: SmartListRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> SmartListRow:
        """Store a particular list."""
        return self._storage.update(new_smart_list, archived_time_action=archived_time_action)

    def load_smart_list(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListRow:
        """Load a particular list by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def load_smart_list_by_key(self, key: SmartListKey, allow_archived: bool = False) -> SmartListRow:
        """Load a particular list by its id."""
        return self._storage.find_first(allow_archived=allow_archived, key=Eq(key))

    def find_all_smart_lists(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> Iterable[SmartListRow]:
        """Load all lists."""
        return self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            key=In(*filter_keys) if filter_keys else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "key": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> SmartListRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return SmartListRow(
            name=typing.cast(str, storage_form["name"]),
            key=SmartListKey(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: SmartListRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "key": live_form.key
        }


@dataclass()
class SmartListTagRow(BaseEntityRow):
    """A tag for a smart list item."""

    smart_list_ref_id: EntityId
    name: Tag


class SmartListTagsRepository:
    """A repository for smart list tags."""

    _SMART_LIST_TAGS_FILE_PATH: ClassVar[Path] = Path("./smart-list-tags.yaml")

    _storage: Final[EntitiesStorage[SmartListTagRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[SmartListTagRow](
            self._SMART_LIST_TAGS_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'SmartListTagsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_smart_list_tag(
            self, smart_list_ref_id: EntityId, name: Tag, archived: bool) -> SmartListTagRow:
        """Create a list tag."""
        all_smart_list_tags_rows_names = frozenset(
            sltr.name.lower()
            for sltr in self._storage.find_all(
                allow_archived=True,
                smart_list_ref_id=In(*smart_list_ref_id) if smart_list_ref_id else None))
        if name.lower() in all_smart_list_tags_rows_names:
            raise ModelValidationError(f'Tag with name "{name}" already exists for smart list')
        new_smart_list_tag = SmartListTagRow(
            smart_list_ref_id=smart_list_ref_id, name=name, archived=archived)
        return self._storage.create(new_smart_list_tag)

    def archive_smart_list_tag(self, ref_id: EntityId) -> SmartListTagRow:
        """Archive a list tag."""
        return self._storage.archive(ref_id)

    def remove_smart_list_tag(self, ref_id: EntityId) -> SmartListTagRow:
        """Hard remove a list tag."""
        return self._storage.remove(ref_id=ref_id)

    def update_smart_list_tag(
            self, new_smart_list_tag: SmartListTagRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> SmartListTagRow:
        """Store a particular list tag."""
        return self._storage.update(new_smart_list_tag, archived_time_action=archived_time_action)

    def load_smart_list_tag(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListTagRow:
        """Load a particular tag item by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_smart_list_tags(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_names: Optional[Iterable[Tag]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListTagRow]:
        """Load all lists tag."""
        return self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            name=In(*filter_names) if filter_names else None,
            smart_list_ref_id=In(*filter_smart_list_ref_ids) if filter_smart_list_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "smart_list_ref_id": {"type": "string"},
            "name": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> SmartListTagRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return SmartListTagRow(
            smart_list_ref_id=EntityId(typing.cast(str, storage_form["smart_list_ref_id"])),
            name=Tag(typing.cast(str, storage_form["name"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: SmartListTagRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "smart_list_ref_id": live_form.smart_list_ref_id,
            "name": live_form.name
        }


@dataclass()
class SmartListItemRow(BaseEntityRow):
    """An item in a smart list."""

    smart_list_ref_id: EntityId
    name: str
    is_done: bool
    tag_ids: Set[EntityId]
    url: Optional[str]


class SmartListItemsRepository:
    """A repository for smart list items."""

    _SMART_LIST_ITEMS_FILE_PATH: ClassVar[Path] = Path("./smart-list-items.yaml")

    _storage: Final[EntitiesStorage[SmartListItemRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[SmartListItemRow](
            self._SMART_LIST_ITEMS_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'SmartListItemsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_smart_list_item(
            self, smart_list_ref_id: EntityId, name: str, is_done: bool, tag_ids: Set[EntityId], url: Optional[str],
            archived: bool) -> SmartListItemRow:
        """Create a list item."""
        new_smart_list_item = SmartListItemRow(
            smart_list_ref_id=smart_list_ref_id, name=name, is_done=is_done, tag_ids=tag_ids, url=url,
            archived=archived)
        return self._storage.create(new_smart_list_item)

    def archive_smart_list_item(self, ref_id: EntityId) -> SmartListItemRow:
        """Archive a list item."""
        return self._storage.archive(ref_id)

    def remove_smart_list_item(self, ref_id: EntityId) -> SmartListItemRow:
        """Hard remove a list item."""
        return self._storage.remove(ref_id=ref_id)

    def update_smart_list_item(
            self, new_smart_list_item: SmartListItemRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> SmartListItemRow:
        """Store a particular list item."""
        return self._storage.update(new_smart_list_item, archived_time_action=archived_time_action)

    def load_smart_list_item(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListItemRow:
        """Load a particular list item by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_smart_list_items(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_is_done: Optional[bool] = None,
            filter_smart_list_tag_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListItemRow]:
        """Load all lists items."""
        return self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            smart_list_ref_id=In(*filter_smart_list_ref_ids) if filter_smart_list_ref_ids else None,
            is_done=Eq(filter_is_done) if filter_is_done else None,
            tag_ids=Intersect(*filter_smart_list_tag_ref_ids) if filter_smart_list_tag_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "smart_list_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "is_done": {"type": "boolean"},
            "tag_ids": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "url": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> SmartListItemRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return SmartListItemRow(
            smart_list_ref_id=EntityId(typing.cast(str, storage_form["smart_list_ref_id"])),
            name=typing.cast(str, storage_form["name"]),
            is_done=typing.cast(bool, storage_form["is_done"]),
            tag_ids=set(EntityId(tid) for tid in typing.cast(List[str], storage_form["tag_ids"])),
            url=typing.cast(str, storage_form["url"]) if storage_form["url"] is not None else None,
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: SmartListItemRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "smart_list_ref_id": live_form.smart_list_ref_id,
            "name": live_form.name,
            "is_done": live_form.is_done,
            "tag_ids": [str(tid) for tid in live_form.tag_ids],
            "url": live_form.url
        }
