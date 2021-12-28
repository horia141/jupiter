"""Repository for smart lists."""
import logging
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Iterable, ClassVar, Final, Set, List

from jupiter.domain.entity_name import EntityName
from jupiter.domain.smart_lists.infra.smart_list_engine import SmartListUnitOfWork, SmartListEngine
from jupiter.domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository, \
    SmartListItemNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository, SmartListAlreadyExistsError, \
    SmartListNotFoundError
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository, SmartListTagNotFoundError
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.url import URL
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.json import JSONDictType
from jupiter.repository.yaml.infra.storage import BaseEntityRow, EntitiesStorage, In, Eq, Intersect,\
    StorageEntityNotFoundError
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _SmartListRow(BaseEntityRow):
    """A container for smart list items."""
    key: SmartListKey
    name: EntityName


class YamlSmartListRepository(SmartListRepository):
    """A repository for lists."""

    _SMART_LISTS_FILE_PATH: ClassVar[Path] = Path("./smart-lists")
    _SMART_LISTS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_SmartListRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_SmartListRow](
            self._SMART_LISTS_FILE_PATH, self._SMART_LISTS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlSmartListRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, smart_list: SmartList) -> SmartList:
        """Create a smart list."""
        smart_list_rows = self._storage.find_all(allow_archived=True, key=Eq(smart_list.key))

        if len(smart_list_rows) > 0:
            raise SmartListAlreadyExistsError(f"Smart list with key='{smart_list.key}' already exists")

        new_smart_list_row = self._storage.create(_SmartListRow(
            archived=smart_list.archived,
            key=smart_list.key,
            name=smart_list.name))
        smart_list.assign_ref_id(new_smart_list_row.ref_id)
        return smart_list

    def save(self, smart_list: SmartList) -> SmartList:
        """Save a smart list - it should already exist."""
        try:
            smart_list_row = self._entity_to_row(smart_list)
            smart_list_row = self._storage.update(smart_list_row)
            return self._row_to_entity(smart_list_row)
        except StorageEntityNotFoundError as err:
            raise SmartListNotFoundError(f"Smart list with key {smart_list.key} does not exist") from err

    def load_by_key(self, key: SmartListKey) -> SmartList:
        """Find a smart list by key."""
        try:
            smart_list_row = self._storage.find_first(allow_archived=False, key=Eq(key))
            return self._row_to_entity(smart_list_row)
        except StorageEntityNotFoundError as err:
            raise SmartListNotFoundError(f"Smart list with key {key} does not exist") from err

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartList:
        """Find a smart list by id."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise SmartListNotFoundError(f"Smart list with id {ref_id} does not exist") from err

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> List[SmartList]:
        """Find all smart lists matching some criteria."""
        return [self._row_to_entity(mr)
                for mr in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
                    key=In(*filter_keys) if filter_keys else None)]

    def remove(self, ref_id: EntityId) -> SmartList:
        """Hard remove a smart list - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise SmartListNotFoundError(f"Smart list with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "key": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _SmartListRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _SmartListRow(
            key=SmartListKey.from_raw(typing.cast(str, storage_form["key"])),
            name=EntityName(typing.cast(str, storage_form["name"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _SmartListRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": str(live_form.name),
            "key": str(live_form.key)
        }

    @staticmethod
    def _entity_to_row(smart_list: SmartList) -> _SmartListRow:
        smart_list_row = _SmartListRow(
            archived=smart_list.archived,
            key=smart_list.key,
            name=smart_list.name)
        smart_list_row.ref_id = smart_list.ref_id
        smart_list_row.created_time = smart_list.created_time
        smart_list_row.archived_time = smart_list.archived_time
        smart_list_row.last_modified_time = smart_list.last_modified_time
        return smart_list_row

    @staticmethod
    def _row_to_entity(row: _SmartListRow) -> SmartList:
        return SmartList(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _key=row.key,
            _name=row.name)


@dataclass()
class _SmartListTagRow(BaseEntityRow):
    """A tag for a smart list item."""

    smart_list_ref_id: EntityId
    tag_name: SmartListTagName


class YamlSmartListTagRepository(SmartListTagRepository):
    """A repository for smart list tags."""

    _SMART_LIST_TAGS_FILE_PATH: ClassVar[Path] = Path("./smart-list-tags")
    _SMART_LIST_TAGS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_SmartListTagRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_SmartListTagRow](
            self._SMART_LIST_TAGS_FILE_PATH, self._SMART_LIST_TAGS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlSmartListTagRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, smart_list_tag: SmartListTag) -> SmartListTag:
        """Create a smart list item."""
        new_smart_list_tag_row = self._storage.create(_SmartListTagRow(
            archived=smart_list_tag.archived,
            smart_list_ref_id=smart_list_tag.smart_list_ref_id,
            tag_name=smart_list_tag.tag_name))
        smart_list_tag.assign_ref_id(new_smart_list_tag_row.ref_id)
        return smart_list_tag

    def save(self, smart_list_tag: SmartListTag) -> SmartListTag:
        """Save a smart list item - it should already exist."""
        try:
            smart_list_tag_row = self._entity_to_row(smart_list_tag)
            smart_list_tag_row = self._storage.update(smart_list_tag_row)
            return self._row_to_entity(smart_list_tag_row)
        except StorageEntityNotFoundError as err:
            raise SmartListTagNotFoundError(f"Smart list tag with id {smart_list_tag.ref_id} does not exist") from err

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListTag:
        """Load a given smart list item."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise SmartListTagNotFoundError(f"Smart list tag with id {ref_id} does not exist") from err

    def find_all_for_smart_list(
            self, smart_list_ref_id: EntityId, allow_archived: bool = False,
            filter_tag_names: Optional[Iterable[SmartListTagName]] = None) -> typing.List[SmartListTag]:
        """Retrieve all smart list items for a given smart list."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    tag_name=In(*filter_tag_names) if filter_tag_names else None,
                    smart_list_ref_id=Eq(smart_list_ref_id))]

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_tag_names: Optional[Iterable[SmartListTagName]] = None) -> typing.List[SmartListTag]:
        """Find all smart list items matching some criteria."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
                    tag_name=In(*(str(fi) for fi in filter_tag_names)) if filter_tag_names else None,
                    smart_list_ref_id=In(*filter_smart_list_ref_ids) if filter_smart_list_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> SmartListTag:
        """Hard remove a smart list - an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise SmartListTagNotFoundError(f"Smart list tag with id {ref_id} does not exist") from err

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "smart_list_ref_id": {"type": "string"},
            "tag_name": {"type": "string"}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _SmartListTagRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _SmartListTagRow(
            smart_list_ref_id=EntityId(typing.cast(str, storage_form["smart_list_ref_id"])),
            tag_name=SmartListTagName.from_raw(typing.cast(str, storage_form["tag_name"])),
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _SmartListTagRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "smart_list_ref_id": str(live_form.smart_list_ref_id),
            "tag_name": str(live_form.tag_name)
        }

    @staticmethod
    def _entity_to_row(smart_list_tag: SmartListTag) -> _SmartListTagRow:
        smart_list_tag_row = _SmartListTagRow(
            archived=smart_list_tag.archived,
            smart_list_ref_id=smart_list_tag.smart_list_ref_id,
            tag_name=smart_list_tag.tag_name)
        smart_list_tag_row.ref_id = smart_list_tag.ref_id
        smart_list_tag_row.created_time = smart_list_tag.created_time
        smart_list_tag_row.archived_time = smart_list_tag.archived_time
        smart_list_tag_row.last_modified_time = smart_list_tag.last_modified_time
        return smart_list_tag_row

    @staticmethod
    def _row_to_entity(row: _SmartListTagRow) -> SmartListTag:
        return SmartListTag(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _smart_list_ref_id=row.smart_list_ref_id,
            _tag_name=row.tag_name)


@dataclass()
class _SmartListItemRow(BaseEntityRow):
    """An item in a smart list."""

    smart_list_ref_id: EntityId
    name: EntityName
    is_done: bool
    tag_ids: Set[EntityId]
    url: Optional[URL]


class YamlSmartListItemRepository(SmartListItemRepository):
    """A repository for smart list items."""

    _SMART_LIST_ITEMS_FILE_PATH: ClassVar[Path] = Path("./smart-list-items")
    _SMART_LIST_ITEMS_NUM_SHARDS: ClassVar[int] = 10

    _storage: Final[EntitiesStorage[_SmartListItemRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_SmartListItemRow](
            self._SMART_LIST_ITEMS_FILE_PATH, self._SMART_LIST_ITEMS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlSmartListItemRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, smart_list_item: SmartListItem) -> SmartListItem:
        """Create a smart listitem."""
        new_smart_list_item_row = self._storage.create(_SmartListItemRow(
            archived=smart_list_item.archived,
            smart_list_ref_id=smart_list_item.smart_list_ref_id,
            name=smart_list_item.name,
            is_done=smart_list_item.is_done,
            tag_ids=set(smart_list_item.tags),
            url=smart_list_item.url))
        smart_list_item.assign_ref_id(new_smart_list_item_row.ref_id)
        return smart_list_item

    def save(self, smart_list_item: SmartListItem) -> SmartListItem:
        """Save a smart listitem - it should already exist."""
        try:
            smart_list_item_row = self._entity_to_row(smart_list_item)
            smart_list_item_row = self._storage.update(smart_list_item_row)
            return self._row_to_entity(smart_list_item_row)
        except StorageEntityNotFoundError as err:
            raise SmartListItemNotFoundError(
                f"Smart list item with id {smart_list_item.ref_id} does not exist") from err

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListItem:
        """Load a given smart listitem."""
        try:
            return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))
        except StorageEntityNotFoundError as err:
            raise SmartListItemNotFoundError(f"Smart list item with id {ref_id} does not exist") from err

    def find_all_for_smart_list(self, smart_list_ref_id: EntityId, allow_archived: bool = False) -> List[SmartListItem]:
        """Retrieve all smart listitems for a given metric."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    smart_list_ref_id=Eq(smart_list_ref_id))]

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_is_done: Optional[bool] = None,
            filter_tag_ref_ids: Optional[Iterable[EntityId]] = None) -> typing.List[SmartListItem]:
        """Find all smart listitems matching some criteria."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
                    smart_list_ref_id=In(*filter_smart_list_ref_ids) if filter_smart_list_ref_ids else None,
                    is_done=Eq(filter_is_done) if filter_is_done else None,
                    tag_ids=Intersect(*filter_tag_ref_ids) if filter_tag_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> SmartListItem:
        """Hard remove a smart list- an irreversible operation."""
        try:
            return self._row_to_entity(self._storage.remove(ref_id=ref_id))
        except StorageEntityNotFoundError as err:
            raise SmartListItemNotFoundError(f"Smart list item with id {ref_id} does not exist") from err

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
    def storage_to_live(storage_form: JSONDictType) -> _SmartListItemRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _SmartListItemRow(
            smart_list_ref_id=EntityId(typing.cast(str, storage_form["smart_list_ref_id"])),
            name=EntityName(typing.cast(str, storage_form["name"])),
            is_done=typing.cast(bool, storage_form["is_done"]),
            tag_ids=set(EntityId(tid) for tid in typing.cast(List[str], storage_form["tag_ids"])),
            url=URL.from_raw(typing.cast(str, storage_form["url"])) if storage_form["url"] is not None else None,
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _SmartListItemRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "smart_list_ref_id": str(live_form.smart_list_ref_id),
            "name": str(live_form.name),
            "is_done": live_form.is_done,
            "tag_ids": [str(tid) for tid in live_form.tag_ids],
            "url": str(live_form.url)
        }

    @staticmethod
    def _entity_to_row(smart_list_item: SmartListItem) -> _SmartListItemRow:
        smart_list_item_row = _SmartListItemRow(
            archived=smart_list_item.archived,
            smart_list_ref_id=smart_list_item.smart_list_ref_id,
            name=smart_list_item.name,
            is_done=smart_list_item.is_done,
            tag_ids=set(smart_list_item.tags),
            url=smart_list_item.url)
        smart_list_item_row.ref_id = smart_list_item.ref_id
        smart_list_item_row.created_time = smart_list_item.created_time
        smart_list_item_row.archived_time = smart_list_item.archived_time
        smart_list_item_row.last_modified_time = smart_list_item.last_modified_time
        return smart_list_item_row

    @staticmethod
    def _row_to_entity(row: _SmartListItemRow) -> SmartListItem:
        return SmartListItem(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _smart_list_ref_id=row.smart_list_ref_id,
            _name=row.name,
            _is_done=row.is_done,
            _tags_ref_id=list(row.tag_ids),
            _url=row.url)


class YamlSmartListUnitOfWork(SmartListUnitOfWork):
    """A Yaml text file specific smart list unit of work."""

    _smart_list_repository: Final[YamlSmartListRepository]
    _smart_list_tag_reposiotry: Final[YamlSmartListTagRepository]
    _smart_list_item_repository: Final[YamlSmartListItemRepository]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._smart_list_repository = YamlSmartListRepository(time_provider)
        self._smart_list_tag_reposiotry = YamlSmartListTagRepository(time_provider)
        self._smart_list_item_repository = YamlSmartListItemRepository(time_provider)

    def __enter__(self) -> 'YamlSmartListUnitOfWork':
        """Enter context."""
        self._smart_list_repository.initialize()
        self._smart_list_tag_reposiotry.initialize()
        self._smart_list_item_repository.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""
        return self._smart_list_repository

    @property
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""
        return self._smart_list_tag_reposiotry

    @property
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""
        return self._smart_list_item_repository


class YamlSmartListEngine(SmartListEngine):
    """An Yaml text file specific smart list engine."""

    _time_provider: Final[TimeProvider]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[SmartListUnitOfWork]:
        """Get the unit of work."""
        yield YamlSmartListUnitOfWork(self._time_provider)
