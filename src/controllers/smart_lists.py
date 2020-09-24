"""The controller for smart lists."""
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from models.basic import EntityId, SmartListKey
from service.smart_lists import SmartListsService, SmartList, SmartListItem


@dataclass()
class LoadAllSmartListsEntry:
    """A single entry in the LoadALlSmartListsResponse."""

    smart_list: SmartList
    smart_list_items: Iterable[SmartListItem]


@dataclass()
class LoadAllSmartListsResponse:
    """Response object for the load_all_smart_lists controller method."""

    smart_lists: Iterable[LoadAllSmartListsEntry]


@dataclass()
class LoadAllSmartListItemsEntry:
    """A single entry in the LoadALlSmartListItemsResponse."""

    smart_list_item: SmartListItem
    smart_list: SmartList


@dataclass()
class LoadAllSmartListItemsResponse:
    """Response object for the load_all_smart_list_items controller method."""

    smart_list_items: Iterable[LoadAllSmartListItemsEntry]


class SmartListsController:
    """The controller for smart lists."""

    _smart_lists_service: Final[SmartListsService]

    def __init__(self, smart_lists_service: SmartListsService) -> None:
        """Controller."""
        self._smart_lists_service = smart_lists_service

    def create_smart_list(self, key: SmartListKey, name: str) -> SmartList:
        """Create a smart list."""
        return self._smart_lists_service.create_smart_list(key=key, name=name)

    def archive_smart_list(self, key: SmartListKey) -> SmartList:
        """Archive smart list item."""
        smart_list = self._smart_lists_service.load_smart_list_by_key(key)
        return self._smart_lists_service.archive_smart_list(smart_list.ref_id)

    def set_smart_list_name(self, key: SmartListKey, name: str) -> SmartList:
        """Change the name of a smart list."""
        smart_list = self._smart_lists_service.load_smart_list_by_key(key)
        return self._smart_lists_service.set_smart_list_name(smart_list.ref_id, name)

    def load_all_smart_lists(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> LoadAllSmartListsResponse:
        """Retrieve all smart lists."""
        smart_lists = self._smart_lists_service.load_all_smart_lists(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_keys=filter_keys)
        smart_list_items = self._smart_lists_service.load_all_smart_list_items(
            allow_archived=allow_archived, filter_smart_list_ref_ids=filter_ref_ids)
        smart_list_items_by_smart_list_ref_ids = {}
        for smart_list_item in smart_list_items:
            if smart_list_item.smart_list_ref_id not in smart_list_items_by_smart_list_ref_ids:
                smart_list_items_by_smart_list_ref_ids[smart_list_item.smart_list_ref_id] = [smart_list_item]
            else:
                smart_list_items_by_smart_list_ref_ids[smart_list_item.smart_list_ref_id].append(smart_list_item)
        return LoadAllSmartListsResponse(
            smart_lists=[LoadAllSmartListsEntry(
                smart_list=sl,
                smart_list_items=smart_list_items_by_smart_list_ref_ids.get(sl.ref_id, [])) for sl in smart_lists])

    def hard_remove_smart_list(self, ref_id: EntityId) -> SmartList:
        """Archive smart list item."""
        return self._smart_lists_service.hard_remove_smart_list(ref_id)

    def create_smart_list_item(self, smart_list_key: SmartListKey, name: str, url: Optional[str]) -> SmartListItem:
        """Create a smart list item."""
        smart_list = self._smart_lists_service.load_smart_list_by_key(smart_list_key)
        return self._smart_lists_service.create_smart_list_item(smart_list.ref_id, name, url)

    def archive_smart_list_item(self, ref_id: EntityId) -> SmartListItem:
        """Archive smart list item."""
        return self._smart_lists_service.archive_smart_list_item(ref_id)

    def set_smart_list_item_name(self, ref_id: EntityId, name: str) -> SmartListItem:
        """Change the name of a smart list item."""
        return self._smart_lists_service.set_smart_list_item_name(ref_id, name)

    def set_smart_list_item_url(self, ref_id: EntityId, url: Optional[str]) -> SmartListItem:
        """Change the url of a smart list item."""
        return self._smart_lists_service.set_smart_list_item_url(ref_id, url)

    def load_all_smart_list_items(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_keys: Optional[Iterable[SmartListKey]] = None) -> LoadAllSmartListItemsResponse:
        """Retrieve all smart list items."""
        smart_lists = self._smart_lists_service.load_all_smart_lists(
            allow_archived=allow_archived, filter_keys=filter_smart_list_keys)
        smart_lists_by_ref_id = {sl.ref_id: sl for sl in smart_lists}
        smart_list_items = self._smart_lists_service.load_all_smart_list_items(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
            filter_smart_list_ref_ids=[sl.ref_id for sl in smart_lists])

        return LoadAllSmartListItemsResponse(
            smart_list_items=[LoadAllSmartListItemsEntry(
                smart_list_item=sl,
                smart_list=smart_lists_by_ref_id[sl.smart_list_ref_id]) for sl in smart_list_items])

    def hard_remove_smart_list_item(self, ref_id: EntityId) -> SmartListItem:
        """Archive smart list item."""
        return self._smart_lists_service.hard_remove_smart_list_item(ref_id)
