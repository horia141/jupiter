"""Repository for smart lists."""
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Iterable, ClassVar, Final
import typing

from models.basic import EntityId, Timestamp, BasicValidator
from repository.common import RepositoryError
from utils.storage import StructuredCollectionStorage, JSONDictType
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartListRow:
    """A container for smart list items."""
    ref_id: EntityId
    name: str
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]


class SmartListsRepository:
    """A repository for lists."""

    _SMART_LISTS_FILE_PATH: ClassVar[Path] = Path("/data/smart-lists.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[SmartListRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._SMART_LISTS_FILE_PATH, self)

    def __enter__(self) -> 'SmartListsRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_smart_list(self, name: str, archived: bool) -> SmartListRow:
        """Create a list."""
        new_smart_list = SmartListRow(
            ref_id=typing.cast(EntityId, None),
            name=name,
            archived=archived,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None)

        self._structured_storage.insert(new_smart_list, set_ref_id=True)

        return new_smart_list

    def archive_smart_list(self, ref_id: EntityId) -> SmartListRow:
        """Archive a list."""
        smart_list = self._structured_storage.find_by_property_strict(ref_id=ref_id)
        smart_list.archived = True
        smart_list.last_modified_time = self._time_provider.get_current_time()
        smart_list.archived_time = self._time_provider.get_current_time()

        self._structured_storage.update(smart_list, ref_id=ref_id)

        return smart_list

    def load_all_smart_lists(
            self, filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListRow]:
        """Load all lists."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        smart_lists = self._structured_storage.find_all_by_property()

        return smart_lists

    def load_smart_list(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListRow:
        """Load a particular list by its id."""
        smart_list = self._structured_storage.find_by_property_strict(ref_id=ref_id)
        if not allow_archived and smart_list.archived:
            raise RepositoryError(f"Smart list with id='{ref_id}' is archived")
        return smart_list

    def save_smart_list(
            self, new_smart_list: SmartListRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> SmartListRow:
        """Store a particular list."""
        new_smart_list.last_modified_time = self._time_provider.get_current_time()
        archived_time_action.act(new_smart_list, "archived_task", self._time_provider.get_current_time())

        self._structured_storage.update(new_smart_list, ref_id=new_smart_list.ref_id)

        return new_smart_list

    def hard_remove_smart_list(self, ref_id: EntityId) -> SmartListRow:
        """Hard remove a smart list."""
        return self._structured_storage.remove(ref_id=ref_id)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "name": {"type": "string"},
                "archived": {"type": "boolean"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> SmartListRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return SmartListRow(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            name=typing.cast(str, storage_form["name"]),
            archived=typing.cast(bool, storage_form["archived"]),
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] is not None else None
        )

    @staticmethod
    def live_to_storage(live_form: SmartListRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "name": live_form.name,
            "archived": live_form.archived,
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time),
            "archived_time": BasicValidator.timestamp_to_str(live_form.archived_time)
                             if live_form.archived_time else None
        }


@dataclass()
class SmartListItemRow:
    """An item in a smart list."""

    ref_id: EntityId
    smart_list_ref_id: EntityId
    name: str
    url: Optional[str]
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]


class SmartListItemsRepository:
    """A repository for smart list items."""

    _SMART_LIST_ITEMS_FILE_PATH: ClassVar[Path] = Path("/data/smart-list-items.yaml")

    _time_provider: Final[TimeProvider]
    _structured_storage: Final[StructuredCollectionStorage[SmartListItemRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._structured_storage = StructuredCollectionStorage(self._SMART_LIST_ITEMS_FILE_PATH, self)

    def __enter__(self) -> 'SmartListItemsRepository':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def create_smart_list_item(
            self, smart_list_ref_id: EntityId, name: str, url: Optional[str], archived: bool) -> SmartListItemRow:
        """Create a list item."""
        new_smart_list_item = SmartListItemRow(
            ref_id=typing.cast(EntityId, None),
            smart_list_ref_id=smart_list_ref_id,
            name=name,
            url=url,
            archived=archived,
            created_time=self._time_provider.get_current_time(),
            last_modified_time=self._time_provider.get_current_time(),
            archived_time=self._time_provider.get_current_time() if archived else None)

        self._structured_storage.insert(new_smart_list_item, set_ref_id=True)
        
        return new_smart_list_item

    def archive_smart_list_item(self, ref_id: EntityId) -> SmartListItemRow:
        """Archive a list item."""
        smart_list_item = self._structured_storage.find_by_property_strict(ref_id=ref_id)
        smart_list_item.archived = True
        smart_list_item.last_modified_time = self._time_provider.get_current_time()
        smart_list_item.archived_time = self._time_provider.get_current_time()

        self._structured_storage.update(smart_list_item, ref_id=ref_id)

        return smart_list_item

    def load_all_smart_list_items(
            self, filter_archived: bool = True,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListItemRow]:
        """Load all lists items."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else []
        filter_smart_list_ref_ids = frozenset(filter_smart_list_ref_ids) if filter_smart_list_ref_ids else []
        smart_list_items = self._structured_storage.find_all_by_property()

        return smart_list_items

    def load_smart_list_item(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListItemRow:
        """Load a particular list item by its id."""
        smart_list_item = self._structured_storage.find_by_property_strict(ref_id=ref_id)
        if not allow_archived and smart_list_item.archived:
            raise RepositoryError(f"Smart list item with id='{ref_id}' is archived")
        return smart_list_item

    def save_smart_list_item(
            self, new_smart_list_item: SmartListItemRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> SmartListItemRow:
        """Store a particular list item."""
        new_smart_list_item.last_modified_time = self._time_provider.get_current_time()
        archived_time_action.act(new_smart_list_item, "archived_task", self._time_provider.get_current_time())

        self._structured_storage.update(new_smart_list_item, ref_id=new_smart_list_item.ref_id)

        return new_smart_list_item

    def hard_remove_smart_list_item(self, ref_id: EntityId) -> SmartListItemRow:
        """Hard remove a list item."""
        return self._structured_storage.remove(ref_id=ref_id)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "smart_list_ref_id": {"type": "string"},
                "name": {"type": "string"},
                "url": {"type": ["string", "null"]},
                "archived": {"type": "boolean"},
                "created_time": {"type": "string"},
                "last_modified_time": {"type": "string"},
                "archived_time": {"type": ["string", "null"]}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> SmartListItemRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return SmartListItemRow(
            ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
            smart_list_ref_id=EntityId(typing.cast(str, storage_form["smart_list_ref_id"])),
            name=typing.cast(str, storage_form["name"]),
            url=typing.cast(str, storage_form["url"]) if storage_form["url"] is not None else None,
            archived=typing.cast(bool, storage_form["archived"]),
            created_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["created_time"])),
            last_modified_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["last_modified_time"])),
            archived_time=BasicValidator.timestamp_from_str(typing.cast(str, storage_form["archived_time"]))
            if storage_form["archived_time"] is not None else None
        )

    @staticmethod
    def live_to_storage(live_form: SmartListItemRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": live_form.ref_id,
            "smart_list_ref_id": live_form.smart_list_ref_id,
            "name": live_form.name,
            "url": live_form.url,
            "archived": live_form.archived,
            "created_time": BasicValidator.timestamp_to_str(live_form.created_time),
            "last_modified_time": BasicValidator.timestamp_to_str(live_form.last_modified_time),
            "archived_time": BasicValidator.timestamp_to_str(live_form.archived_time)
                             if live_form.archived_time else None
        }
